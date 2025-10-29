from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import ProctoringLog, TestAttempt, User
from app.schemas import FrameAnalysisRequest, ProctoringLogResponse
from app.services.proctoring_service import proctoring_service

router = APIRouter()

# In-memory waiting room storage (in production, use Redis)
waiting_room = {}  # {test_id: {student_id: {status, violations, timestamp}}}

class WaitingRoomAction(BaseModel):
    student_id: int
    action: str  # 'admit', 'pause', 'terminate'
    
class ViolationReport(BaseModel):
    attempt_id: int
    violation_type: str
    severity: str
    violation_score: int
    details: str

@router.post("/analyze-frame")
async def analyze_frame(
    request: FrameAnalysisRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TestAttempt).where(TestAttempt.id == request.attempt_id)
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test attempt not found"
        )
    
    if attempt.student_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    analysis = await proctoring_service.analyze_frame(request.frame_base64)
    
    for violation in analysis["violations"]:
        log = ProctoringLog(
            attempt_id=request.attempt_id,
            student_id=user.id,
            violation_type=violation["type"],
            severity=violation["severity"],
            description=violation["description"],
            log_metadata={
                "face_count": analysis["face_count"],
                "head_pose": analysis["head_pose"],
                "gaze_direction": analysis["gaze_direction"],
            }
        )
        db.add(log)
        attempt.proctoring_violations += 1
    
    if analysis["violations"]:
        await db.flush()
    
    return analysis

@router.get("/violations/{attempt_id}", response_model=List[ProctoringLogResponse])
async def get_violations(
    attempt_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TestAttempt).where(TestAttempt.id == attempt_id)
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test attempt not found"
        )
    
    result = await db.execute(
        select(ProctoringLog)
        .where(ProctoringLog.attempt_id == attempt_id)
        .order_by(ProctoringLog.timestamp.desc())
    )
    logs = result.scalars().all()
    
    return logs

@router.get("/summary/{attempt_id}")
async def get_proctoring_summary(
    attempt_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ProctoringLog).where(ProctoringLog.attempt_id == attempt_id)
    )
    logs = result.scalars().all()
    
    summary = {
        "total_violations": len(logs),
        "critical": sum(1 for log in logs if log.severity == "critical"),
        "high": sum(1 for log in logs if log.severity == "high"),
        "medium": sum(1 for log in logs if log.severity == "medium"),
        "low": sum(1 for log in logs if log.severity == "low"),
        "violation_types": {}
    }
    
    for log in logs:
        if log.violation_type not in summary["violation_types"]:
            summary["violation_types"][log.violation_type] = 0
        summary["violation_types"][log.violation_type] += 1
    
    return summary

# WAITING ROOM ENDPOINTS - Teacher has supreme power

@router.post("/send-to-waiting-room")
async def send_to_waiting_room(
    report: ViolationReport,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Student exceeded violation threshold - send to waiting room"""
    
    result = await db.execute(
        select(TestAttempt).where(TestAttempt.id == report.attempt_id)
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    if attempt.student_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get test_id from attempt
    test_id = attempt.test_id
    
    # Initialize test waiting room if doesn't exist
    if test_id not in waiting_room:
        waiting_room[test_id] = {}
    
    # Add student to waiting room
    waiting_room[test_id][user.id] = {
        'student_id': user.id,
        'student_name': user.full_name,
        'student_number': user.student_id,
        'attempt_id': report.attempt_id,
        'status': 'waiting',  # waiting, admitted, paused, terminated
        'violation_score': report.violation_score,
        'violation_type': report.violation_type,
        'details': report.details,
        'timestamp': str(__import__('datetime').datetime.now()),
        'paused': False,
        'test_state': None  # Will store answers when paused
    }
    
    # Log the severe violation
    log = ProctoringLog(
        attempt_id=report.attempt_id,
        student_id=user.id,
        violation_type=report.violation_type,
        severity=report.severity,
        description=f"SENT TO WAITING ROOM: {report.details}"
    )
    db.add(log)
    await db.commit()
    
    print(f"🚨 Student {user.full_name} sent to waiting room for test {test_id}")
    print(f"   Violation: {report.violation_type} (Score: {report.violation_score})")
    
    return {
        "status": "sent_to_waiting_room",
        "message": f"Excessive violations detected. Total score: {report.violation_score}",
        "waiting_room_status": waiting_room[test_id][user.id]
    }

@router.get("/waiting-room/{test_id}")
async def get_waiting_room(
    test_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all students in waiting room for a test - Teacher only"""
    
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    
    if test_id not in waiting_room:
        return {"students": []}
    
    return {
        "students": list(waiting_room[test_id].values())
    }

@router.get("/waiting-room-status/{test_id}/{student_id}")
async def check_waiting_room_status(
    test_id: int,
    student_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Student checks their waiting room status"""
    
    if user.id != student_id and user.role != "teacher":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if test_id not in waiting_room or student_id not in waiting_room[test_id]:
        return {"in_waiting_room": False, "status": None}
    
    return {
        "in_waiting_room": True,
        "status": waiting_room[test_id][student_id]['status'],
        "details": waiting_room[test_id][student_id]
    }

@router.post("/teacher-action/{test_id}")
async def teacher_waiting_room_action(
    test_id: int,
    action: WaitingRoomAction,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Teacher controls student - SUPREME POWER"""
    
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only - Supreme power!")
    
    if test_id not in waiting_room or action.student_id not in waiting_room[test_id]:
        raise HTTPException(status_code=404, detail="Student not in waiting room")
    
    student_data = waiting_room[test_id][action.student_id]
    
    if action.action == "admit":
        # Let student back in
        student_data['status'] = 'admitted'
        student_data['paused'] = False
        message = f"Teacher admitted student back into test"
        
    elif action.action == "pause":
        # Pause student's test
        student_data['status'] = 'paused'
        student_data['paused'] = True
        message = f"Teacher paused student's test"
        
    elif action.action == "terminate":
        # Terminate student's test
        student_data['status'] = 'terminated'
        
        # Update test attempt
        result = await db.execute(
            select(TestAttempt).where(TestAttempt.id == student_data['attempt_id'])
        )
        attempt = result.scalar_one_or_none()
        
        if attempt:
            attempt.status = 'terminated'
            attempt.end_time = __import__('datetime').datetime.now()
            await db.commit()
        
        # Remove from waiting room
        del waiting_room[test_id][action.student_id]
        message = f"Teacher terminated student's test"
        
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    print(f"👨‍🏫 TEACHER ACTION: {action.action.upper()} student {action.student_id} in test {test_id}")
    
    return {
        "status": "success",
        "action": action.action,
        "message": message,
        "student_status": student_data if action.action != "terminate" else None
    }

@router.post("/report-violation")
async def report_violation(
    report: ViolationReport,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Log any violation from frontend"""
    
    result = await db.execute(
        select(TestAttempt).where(TestAttempt.id == report.attempt_id)
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Test attempt not found")
    
    if attempt.student_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Log violation
    log = ProctoringLog(
        attempt_id=report.attempt_id,
        student_id=user.id,
        violation_type=report.violation_type,
        severity=report.severity,
        description=report.details
    )
    db.add(log)
    attempt.proctoring_violations += 1
    await db.commit()
    
    return {"status": "logged", "total_violations": attempt.proctoring_violations}
