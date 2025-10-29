from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
import secrets
import string

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import AIContent, User, Test, Question, TestType
from app.schemas import (
    AIContentRequest,
    AIContentResponse,
    AIQuizGenerate,
    AIQuizResponse,
    TestResponse,
    QuestionResponse
)
from app.services.ai_service import ai_service

router = APIRouter()

# Course Generation Schemas
class CourseGenerateRequest(BaseModel):
    topic: str
    duration_days: int
    difficulty: str = "medium"
    learning_style: str = "comprehensive"

class DayContentRequest(BaseModel):
    topic: str
    day_number: int
    lesson_title: str
    objectives: List[str]

class AssessmentRequest(BaseModel):
    topic: str
    day_number: int
    covered_topics: List[str]
    num_questions: int = 5
    difficulty: str = "medium"

def generate_test_code() -> str:
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

@router.post("/generate-content", response_model=AIContentResponse)
async def generate_content(
    request: AIContentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        content = await ai_service.generate_learning_content(
            topic=request.topic,
            content_type=request.content_type,
            difficulty=request.difficulty
        )
        
        ai_content = AIContent(
            user_id=user.id,
            topic=request.topic,
            content_type=request.content_type,
            content=content,
            content_metadata={"difficulty": request.difficulty}
        )
        
        db.add(ai_content)
        await db.flush()
        await db.refresh(ai_content)
        
        return ai_content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}"
        )

@router.post("/generate-quiz", response_model=AIQuizResponse)
async def generate_quiz(
    request: AIQuizGenerate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        questions = await ai_service.generate_quiz_questions(
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        
        return AIQuizResponse(
            topic=request.topic,
            questions=questions
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.post("/create-ai-test", response_model=TestResponse)
async def create_ai_test(
    request: AIQuizGenerate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create tests"
        )
    
    try:
        questions_data = await ai_service.generate_quiz_questions(
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        
        total_marks = sum(q["marks"] for q in questions_data)
        
        test = Test(
            title=f"AI Quiz: {request.topic}",
            description=f"AI-generated {request.difficulty} level quiz on {request.topic}",
            test_type=TestType.AI_GENERATED,
            test_code=generate_test_code(),
            duration_minutes=request.num_questions * 2,
            total_marks=total_marks,
            passing_marks=int(total_marks * 0.6),
            proctoring_enabled=False,
            ai_topic=request.topic,
            difficulty_level=request.difficulty,
            creator_id=user.id
        )
        
        db.add(test)
        await db.flush()
        
        for idx, q_data in enumerate(questions_data):
            question = Question(
                test_id=test.id,
                question_type=q_data["question_type"],
                question_text=q_data["question_text"],
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                marks=q_data["marks"],
                difficulty=q_data.get("difficulty", request.difficulty),
                order_index=idx
            )
            db.add(question)
        
        await db.flush()
        
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        
        result = await db.execute(
            select(Test).where(Test.id == test.id).options(selectinload(Test.questions))
        )
        test = result.scalar_one()
        
        return test
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI test: {str(e)}"
        )

# New Course Generation Endpoints
@router.post("/generate-course")
async def generate_course(
    request: CourseGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a complete course curriculum with daily lessons"""
    try:
        course_data = await ai_service.generate_course(
            topic=request.topic,
            duration_days=request.duration_days,
            difficulty=request.difficulty,
            learning_style=request.learning_style
        )
        
        # Store course in AI Content
        ai_content = AIContent(
            user_id=user.id,
            topic=request.topic,
            content_type="course",
            content=str(course_data),
            content_metadata={
                "duration_days": request.duration_days,
                "difficulty": request.difficulty,
                "learning_style": request.learning_style
            }
        )
        
        db.add(ai_content)
        await db.flush()
        
        return {
            "success": True,
            "course": course_data,
            "content_id": ai_content.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate course: {str(e)}"
        )

@router.post("/generate-day-content")
async def generate_day_content(
    request: DayContentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate detailed content for a specific day's lesson"""
    try:
        content = await ai_service.generate_day_content(
            topic=request.topic,
            day_number=request.day_number,
            lesson_title=request.lesson_title,
            objectives=request.objectives
        )
        
        # Store day content
        ai_content = AIContent(
            user_id=user.id,
            topic=f"{request.topic} - Day {request.day_number}",
            content_type="lesson",
            content=content,
            content_metadata={
                "day_number": request.day_number,
                "lesson_title": request.lesson_title,
                "objectives": request.objectives
            }
        )
        
        db.add(ai_content)
        await db.flush()
        
        return {
            "success": True,
            "day_number": request.day_number,
            "lesson_title": request.lesson_title,
            "content": content,
            "content_id": ai_content.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate day content: {str(e)}"
        )

@router.post("/generate-assessment")
async def generate_assessment(
    request: AssessmentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate assessment questions for covered topics"""
    try:
        questions = await ai_service.generate_assessment(
            topic=request.topic,
            day_number=request.day_number,
            covered_topics=request.covered_topics,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        
        return {
            "success": True,
            "day_number": request.day_number,
            "questions": questions,
            "total_marks": sum(q["marks"] for q in questions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate assessment: {str(e)}"
        )

@router.post("/create-course-test")
async def create_course_test(
    request: AssessmentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a test from assessment questions and save to database"""
    try:
        questions_data = await ai_service.generate_assessment(
            topic=request.topic,
            day_number=request.day_number,
            covered_topics=request.covered_topics,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        
        total_marks = sum(q["marks"] for q in questions_data)
        
        test = Test(
            title=f"{request.topic} - Day {request.day_number} Assessment",
            description=f"Assessment covering: {', '.join(request.covered_topics)}",
            test_type=TestType.AI_GENERATED,
            test_code=generate_test_code(),
            duration_minutes=request.num_questions * 3,
            total_marks=total_marks,
            passing_marks=int(total_marks * 0.6),
            proctoring_enabled=True,
            enable_face_detection=True,
            enable_tab_switch_detection=True,
            ai_topic=request.topic,
            difficulty_level=request.difficulty,
            creator_id=user.id
        )
        
        db.add(test)
        await db.flush()
        
        for idx, q_data in enumerate(questions_data):
            question = Question(
                test_id=test.id,
                question_type=q_data["question_type"],
                question_text=q_data["question_text"],
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                marks=q_data["marks"],
                difficulty=q_data.get("difficulty", request.difficulty),
                order_index=idx
            )
            db.add(question)
        
        await db.flush()
        
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        
        result = await db.execute(
            select(Test).where(Test.id == test.id).options(selectinload(Test.questions))
        )
        test = result.scalar_one()
        
        return {
            "success": True,
            "test": test,
            "test_id": test.id,
            "test_code": test.test_code
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create course test: {str(e)}"
        )

@router.get("/my-courses")
async def get_my_courses(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all courses generated by the current user"""
    from sqlalchemy import select, desc
    
    try:
        result = await db.execute(
            select(AIContent)
            .where(AIContent.user_id == user.id)
            .where(AIContent.content_type == "course")
            .order_by(desc(AIContent.created_at))
        )
        courses = result.scalars().all()
        
        # Parse course data from content
        courses_list = []
        for course in courses:
            try:
                import ast
                course_data = ast.literal_eval(course.content)
                courses_list.append({
                    "id": course.id,
                    "topic": course.topic,
                    "created_at": course.created_at,
                    "metadata": course.content_metadata,
                    "course_title": course_data.get("course_title", course.topic),
                    "description": course_data.get("description", ""),
                    "total_days": course_data.get("total_days", 0),
                    "difficulty": course_data.get("difficulty", "medium"),
                    "daily_lessons_count": len(course_data.get("daily_lessons", []))
                })
            except:
                # Fallback if parsing fails
                courses_list.append({
                    "id": course.id,
                    "topic": course.topic,
                    "created_at": course.created_at,
                    "metadata": course.content_metadata,
                    "course_title": course.topic,
                    "description": "AI-generated course",
                    "total_days": course.content_metadata.get("duration_days", 0),
                    "difficulty": course.content_metadata.get("difficulty", "medium"),
                    "daily_lessons_count": 0
                })
        
        return {
            "success": True,
            "courses": courses_list,
            "total": len(courses_list)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch courses: {str(e)}"
        )

@router.get("/course/{course_id}")
async def get_course_detail(
    course_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed course data by ID"""
    from sqlalchemy import select
    
    try:
        result = await db.execute(
            select(AIContent)
            .where(AIContent.id == course_id)
            .where(AIContent.user_id == user.id)
            .where(AIContent.content_type == "course")
        )
        course = result.scalar_one_or_none()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        import ast
        course_content = ast.literal_eval(course.content)
        
        return {
            "success": True,
            "course": {
                "id": course.id,
                "topic": course.topic,
                "content": course_content,
                "created_at": course.created_at
            },
            "metadata": course.content_metadata or {}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch course: {str(e)}"
        )
