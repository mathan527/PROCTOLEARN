from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import secrets
import string

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Test, Question, User, TestAttempt, TestType
from app.schemas import TestCreate, TestResponse, TestUpdate, TestAttemptStart, TestAttemptResponse

router = APIRouter()

def generate_test_code() -> str:
    """Generate a unique 4-digit test code"""
    return ''.join(secrets.choice(string.digits) for _ in range(4))

@router.post("/create")
async def create_test(
    test_data: TestCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new test with questions"""
    if user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create tests"
        )
    
    # Generate unique 4-digit code
    test_code = generate_test_code()
    
    # Ensure code is unique
    while True:
        result = await db.execute(
            select(Test).where(Test.test_code == test_code)
        )
        if not result.scalar_one_or_none():
            break
        test_code = generate_test_code()
    
    test = Test(
        title=test_data.title,
        description=test_data.description,
        test_type=TestType.TEACHER_CREATED,
        test_code=test_code,
        duration_minutes=test_data.duration_minutes,
        total_marks=test_data.total_marks,
        passing_marks=test_data.passing_marks,
        proctoring_enabled=test_data.proctoring_enabled,
        allow_tab_switch=test_data.allow_tab_switch,
        require_webcam=test_data.require_webcam,
        detect_multiple_faces=test_data.detect_multiple_faces,
        start_time=test_data.start_time,
        end_time=test_data.end_time,
        creator_id=user.id
    )
    
    db.add(test)
    await db.flush()
    
    for idx, q_data in enumerate(test_data.questions):
        question = Question(
            test_id=test.id,
            question_type=q_data.question_type,
            question_text=q_data.question_text,
            options=q_data.options,
            correct_answer=q_data.correct_answer,
            marks=q_data.marks,
            difficulty=q_data.difficulty,
            order_index=idx
        )
        db.add(question)
    
    await db.flush()
    await db.refresh(test)
    
    return {
        "success": True,
        "test_id": test.id,
        "test_code": test.test_code,
        "message": "Test created successfully"
    }

@router.post("/", response_model=TestResponse)
async def create_test(
    test_data: TestCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create tests"
        )
    
    test = Test(
        title=test_data.title,
        description=test_data.description,
        test_type=TestType.TEACHER_CREATED,
        test_code=generate_test_code(),
        duration_minutes=test_data.duration_minutes,
        total_marks=test_data.total_marks,
        passing_marks=test_data.passing_marks,
        proctoring_enabled=test_data.proctoring_enabled,
        allow_tab_switch=test_data.allow_tab_switch,
        require_webcam=test_data.require_webcam,
        detect_multiple_faces=test_data.detect_multiple_faces,
        start_time=test_data.start_time,
        end_time=test_data.end_time,
        creator_id=user.id
    )
    
    db.add(test)
    await db.flush()
    
    for idx, q_data in enumerate(test_data.questions):
        question = Question(
            test_id=test.id,
            question_type=q_data.question_type,
            question_text=q_data.question_text,
            question_image_url=q_data.question_image_url,
            options=q_data.options,
            correct_answer=q_data.correct_answer,
            marks=q_data.marks,
            difficulty=q_data.difficulty,
            order_index=idx
        )
        db.add(question)
    
    await db.flush()
    await db.refresh(test)
    
    result = await db.execute(
        select(Test).where(Test.id == test.id).options(selectinload(Test.questions))
    )
    test = result.scalar_one()
    
    return test

@router.get("/my-tests", response_model=List[TestResponse])
async def get_my_tests(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user.role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot access this endpoint"
        )
    
    result = await db.execute(
        select(Test)
        .where(Test.creator_id == user.id)
        .options(selectinload(Test.questions))
        .order_by(Test.created_at.desc())
    )
    tests = result.scalars().all()
    
    return tests

@router.get("/{test_id}", response_model=TestResponse)
async def get_test(
    test_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Test)
        .where(Test.id == test_id)
        .options(selectinload(Test.questions))
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    return test

@router.put("/{test_id}", response_model=TestResponse)
async def update_test(
    test_id: int,
    test_data: TestUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Test).where(Test.id == test_id))
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    if test.creator_id != user.id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this test"
        )
    
    for key, value in test_data.model_dump(exclude_unset=True).items():
        setattr(test, key, value)
    
    await db.flush()
    await db.refresh(test)
    
    return test

@router.delete("/{test_id}")
async def delete_test(
    test_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Test).where(Test.id == test_id))
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    if test.creator_id != user.id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this test"
        )
    
    await db.delete(test)
    await db.flush()
    
    return {"message": "Test deleted successfully"}

@router.get("/validate-code/{test_code}")
async def validate_test_code(
    test_code: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate test code and return test info without starting attempt"""
    # Allow both students and teachers (teachers can test their own tests)
    
    result = await db.execute(
        select(Test)
        .where(Test.test_code == test_code)
        .options(selectinload(Test.questions))
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid test code"
        )
    
    if not test.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This test is no longer active"
        )
    
    return {
        "success": True,
        "test": {
            "id": test.id,
            "title": test.title,
            "description": test.description,
            "duration_minutes": test.duration_minutes,
            "total_marks": test.total_marks,
            "question_count": len(test.questions),
            "proctoring_enabled": test.proctoring_enabled,
            "require_webcam": test.require_webcam,
            "detect_multiple_faces": test.detect_multiple_faces,
            "allow_tab_switch": test.allow_tab_switch
        }
    }

@router.post("/start-attempt", response_model=TestAttemptResponse)
async def start_test_attempt(
    request: TestAttemptStart,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a test attempt after validation"""
    # Allow both students and teachers (for testing purposes)
    
    result = await db.execute(
        select(Test).where(Test.test_code == request.test_code)
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found with this code"
        )
    
    if not test.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This test is no longer active"
        )
    
    # Check for existing attempt
    result = await db.execute(
        select(TestAttempt).where(
            TestAttempt.test_id == test.id,
            TestAttempt.student_id == user.id,
            TestAttempt.status == "in_progress"
        )
    )
    existing_attempt = result.scalar_one_or_none()
    
    if existing_attempt:
        await db.refresh(existing_attempt)
        return existing_attempt
    
    attempt = TestAttempt(
        test_id=test.id,
        student_id=user.id,
        status="in_progress"
    )
    
    db.add(attempt)
    await db.flush()
    await db.refresh(attempt)
    
    # Add admission_mode to response
    attempt_dict = {
        "id": attempt.id,
        "test_id": attempt.test_id,
        "student_id": attempt.student_id,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "time_taken_minutes": attempt.time_taken_minutes,
        "total_score": attempt.total_score,
        "percentage": attempt.percentage,
        "status": attempt.status,
        "proctoring_violations": attempt.proctoring_violations,
        "admission_mode": test.admission_mode.value if test.admission_mode else "auto_admit"
    }
    
    return attempt_dict

@router.post("/start", response_model=TestAttemptResponse)
async def start_test(
    test_code_data: TestAttemptStart,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can take tests"
        )
    
    result = await db.execute(
        select(Test).where(Test.test_code == test_code_data.test_code)
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found with this code"
        )
    
    if not test.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This test is no longer active"
        )
    
    result = await db.execute(
        select(TestAttempt).where(
            TestAttempt.test_id == test.id,
            TestAttempt.student_id == user.id,
            TestAttempt.status == "in_progress"
        )
    )
    existing_attempt = result.scalar_one_or_none()
    
    if existing_attempt:
        return existing_attempt
    
    attempt = TestAttempt(
        test_id=test.id,
        student_id=user.id,
        status="in_progress"
    )
    
    db.add(attempt)
    await db.flush()
    await db.refresh(attempt)
    
    return attempt
