from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Test, Question, TestAttempt, Answer, User
from app.schemas import AnswerSubmit, TestAttemptResponse, QuestionResponse

router = APIRouter()

@router.get("/test/{test_id}", response_model=List[QuestionResponse])
async def get_test_questions(
    test_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Question)
        .where(Question.test_id == test_id)
        .order_by(Question.order_index)
    )
    questions = result.scalars().all()
    
    return questions

@router.post("/submit-answer")
async def submit_answer(
    answer_data: AnswerSubmit,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TestAttempt).where(
            TestAttempt.student_id == user.id,
            TestAttempt.status == "in_progress"
        ).order_by(TestAttempt.started_at.desc())
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active test attempt found"
        )
    
    result = await db.execute(
        select(Question).where(Question.id == answer_data.question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    result = await db.execute(
        select(Answer).where(
            Answer.attempt_id == attempt.id,
            Answer.question_id == answer_data.question_id
        )
    )
    existing_answer = result.scalar_one_or_none()
    
    if existing_answer:
        existing_answer.answer_text = answer_data.answer_text
        answer = existing_answer
    else:
        answer = Answer(
            attempt_id=attempt.id,
            question_id=answer_data.question_id,
            answer_text=answer_data.answer_text
        )
        db.add(answer)
    
    await db.flush()
    
    return {"message": "Answer saved successfully"}

@router.post("/submit-test/{attempt_id}", response_model=TestAttemptResponse)
async def submit_test(
    attempt_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.id == attempt_id)
        .options(selectinload(TestAttempt.answers), selectinload(TestAttempt.test))
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
    
    if attempt.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test already submitted"
        )
    
    result = await db.execute(
        select(Question).where(Question.test_id == attempt.test_id)
    )
    questions = result.scalars().all()
    
    total_score = 0.0
    for answer in attempt.answers:
        question = next((q for q in questions if q.id == answer.question_id), None)
        if question:
            if question.question_type in ["multiple_choice", "true_false"]:
                if answer.answer_text.strip().upper() == question.correct_answer.strip().upper():
                    answer.is_correct = True
                    answer.marks_obtained = question.marks
                    total_score += question.marks
                else:
                    answer.is_correct = False
                    answer.marks_obtained = 0
            else:
                answer.is_correct = None
                answer.marks_obtained = None
    
    attempt.submitted_at = datetime.utcnow()
    attempt.time_taken_minutes = int((attempt.submitted_at - attempt.started_at).total_seconds() / 60)
    attempt.total_score = total_score
    attempt.percentage = (total_score / attempt.test.total_marks * 100) if attempt.test.total_marks > 0 else 0
    attempt.status = "submitted"
    
    await db.flush()
    await db.refresh(attempt)
    
    return attempt
