from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class TestType(str, enum.Enum):
    TEACHER_CREATED = "teacher_created"
    AI_GENERATED = "ai_generated"

class AdmissionMode(str, enum.Enum):
    AUTO_ADMIT = "auto_admit"
    MANUAL_APPROVAL = "manual_approval"

class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    
    student_id = Column(String(50), unique=True, nullable=True)
    department = Column(String(100), nullable=True)
    semester = Column(Integer, nullable=True)
    
    employee_id = Column(String(50), unique=True, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_tests = relationship("Test", back_populates="creator", foreign_keys="Test.creator_id")
    test_attempts = relationship("TestAttempt", back_populates="student")
    ai_content_requests = relationship("AIContent", back_populates="user")
    proctoring_logs = relationship("ProctoringLog", back_populates="student")

class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    test_type = Column(Enum(TestType), nullable=False)
    test_code = Column(String(10), unique=True, index=True, nullable=False)
    
    duration_minutes = Column(Integer, nullable=False)
    total_marks = Column(Integer, nullable=False)
    passing_marks = Column(Integer, nullable=False)
    
    proctoring_enabled = Column(Boolean, default=False)
    allow_tab_switch = Column(Boolean, default=False)
    require_webcam = Column(Boolean, default=False)
    detect_multiple_faces = Column(Boolean, default=False)
    admission_mode = Column(Enum(AdmissionMode), default=AdmissionMode.AUTO_ADMIT)
    
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    ai_topic = Column(String(255), nullable=True)
    difficulty_level = Column(String(20), nullable=True)
    
    is_active = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("User", back_populates="created_tests", foreign_keys=[creator_id])
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    attempts = relationship("TestAttempt", back_populates="test", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    
    question_type = Column(Enum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    question_image_url = Column(String(500), nullable=True)
    
    options = Column(JSON, nullable=True)
    correct_answer = Column(String(500), nullable=False)
    
    marks = Column(Integer, nullable=False, default=1)
    difficulty = Column(String(20), nullable=True)
    
    order_index = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test = relationship("Test", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

class TestAttempt(Base):
    __tablename__ = "test_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    time_taken_minutes = Column(Integer, nullable=True)
    
    total_score = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)
    status = Column(String(20), default="in_progress")
    
    proctoring_violations = Column(Integer, default=0)
    proctoring_summary = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    test = relationship("Test", back_populates="attempts")
    student = relationship("User", back_populates="test_attempts")
    answers = relationship("Answer", back_populates="attempt", cascade="all, delete-orphan")
    proctoring_logs = relationship("ProctoringLog", back_populates="attempt", cascade="all, delete-orphan")

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    answer_text = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    marks_obtained = Column(Float, nullable=True)
    
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    attempt = relationship("TestAttempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")

class AIContent(Base):
    __tablename__ = "ai_content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    topic = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    
    content = Column(Text, nullable=False)
    content_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="ai_content_requests")

class ProctoringLog(Base):
    __tablename__ = "proctoring_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    violation_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    
    snapshot_url = Column(String(500), nullable=True)
    log_metadata = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    attempt = relationship("TestAttempt", back_populates="proctoring_logs")
    student = relationship("User", back_populates="proctoring_logs")
