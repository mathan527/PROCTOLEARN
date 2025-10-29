from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    student_id: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    employee_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    student_id: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    employee_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuestionCreate(BaseModel):
    question_type: QuestionType
    question_text: str
    question_image_url: Optional[str] = None
    options: Optional[List[str]] = None  # Changed from Dict to List
    correct_answer: str
    marks: int = 1
    difficulty: Optional[str] = None

class QuestionResponse(BaseModel):
    id: int
    test_id: int
    question_type: QuestionType
    question_text: str
    question_image_url: Optional[str] = None
    options: Optional[List[str]] = None  # Changed from Dict to List
    correct_answer: str
    marks: int
    difficulty: Optional[str] = None
    order_index: int
    
    class Config:
        from_attributes = True

class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    total_marks: int
    passing_marks: int
    proctoring_enabled: bool = False
    allow_tab_switch: bool = False
    require_webcam: bool = False
    detect_multiple_faces: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    questions: List[QuestionCreate] = []

class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    total_marks: Optional[int] = None
    passing_marks: Optional[int] = None
    proctoring_enabled: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None

class TestResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    test_code: str
    duration_minutes: int
    total_marks: int
    passing_marks: int
    proctoring_enabled: bool
    allow_tab_switch: bool
    require_webcam: bool
    detect_multiple_faces: bool
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool
    creator_id: int
    created_at: datetime
    questions: List[QuestionResponse] = []
    
    class Config:
        from_attributes = True

class TestAttemptStart(BaseModel):
    test_code: str

class TestAttemptResponse(BaseModel):
    id: int
    test_id: int
    student_id: int
    started_at: datetime
    submitted_at: Optional[datetime] = None
    time_taken_minutes: Optional[int] = None
    total_score: Optional[float] = None
    percentage: Optional[float] = None
    status: str
    proctoring_violations: int
    admission_mode: Optional[str] = None
    
    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str

class AIContentRequest(BaseModel):
    topic: str
    content_type: str
    difficulty: Optional[str] = "medium"

class AIContentResponse(BaseModel):
    id: int
    topic: str
    content_type: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AIQuizGenerate(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"

class AIQuizResponse(BaseModel):
    topic: str
    questions: List[QuestionCreate]

class ProctoringViolation(BaseModel):
    violation_type: str
    severity: str
    description: str

class ProctoringLogResponse(BaseModel):
    id: int
    attempt_id: int
    student_id: int
    violation_type: str
    severity: str
    description: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class FrameAnalysisRequest(BaseModel):
    attempt_id: int
    frame_base64: str
