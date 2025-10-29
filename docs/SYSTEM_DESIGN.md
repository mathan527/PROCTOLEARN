# ProtoLearn - System Design

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          CLIENT TIER                                  │
│  ┌────────────────────┐  ┌────────────────────┐  ┌─────────────────┐ │
│  │  Student Browser   │  │  Teacher Browser   │  │  Admin Browser  │ │
│  │  - Vue 3 App       │  │  - Vue 3 App       │  │  - Vue 3 App    │ │
│  │  - WebRTC Client   │  │  - WebRTC Monitor  │  │  - Analytics    │ │
│  │  - TensorFlow.js   │  │  - Socket.IO       │  │  - User Mgmt    │ │
│  └────────┬───────────┘  └──────────┬─────────┘  └────────┬────────┘ │
└───────────┼──────────────────────────┼─────────────────────┼──────────┘
            │                          │                     │
            │ HTTPS/WSS               │ HTTPS/WSS           │ HTTPS
            ▼                          ▼                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       APPLICATION TIER                                │
│  ┌──────────────────────────────────────────────────────────────────┐│
│  │               FastAPI Application (Granian)                       ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  ││
│  │  │  REST API    │  │  WebSocket   │  │  AI Service Layer    │  ││
│  │  │  Endpoints   │  │  Signaling   │  │  - Groq Client       │  ││
│  │  │              │  │  Server      │  │  - DeepSeek Client   │  ││
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  ││
│  │         │                  │                     │              ││
│  │  ┌──────▼──────────────────▼─────────────────────▼───────────┐ ││
│  │  │            Business Logic Layer                            │ ││
│  │  │  - Authentication  - Test Management  - AI Question Gen   │ ││
│  │  │  - Proctoring      - User Management  - Teaching Assistant│ ││
│  │  └────────────────────────┬───────────────────────────────────┘ ││
│  └───────────────────────────┼─────────────────────────────────────┘│
└────────────────────────────────┼───────────────────────────────────────┘
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
┌────────────────────────────────┐  ┌──────────────────────────┐
│       DATA TIER                │  │    EXTERNAL SERVICES     │
│  ┌──────────────────────────┐  │  │  ┌────────────────────┐  │
│  │  PostgreSQL (Cloud)      │  │  │  │  Groq API          │  │
│  │  - Users                 │  │  │  │  (Question Gen)    │  │
│  │  - Tests                 │  │  │  └────────────────────┘  │
│  │  - Questions             │  │  │  ┌────────────────────┐  │
│  │  - Attempts              │  │  │  │  DeepSeek OCR      │  │
│  │  - Violations            │  │  │  │  (Text Extract)    │  │
│  │  - Learning Materials    │  │  │  └────────────────────┘  │
│  └──────────────────────────┘  │  │  ┌────────────────────┐  │
└────────────────────────────────┘  │  │  Google STUN       │  │
                                    │  │  (WebRTC NAT)      │  │
                                    │  └────────────────────┘  │
                                    └──────────────────────────┘
```

---

## Component Architecture

### 1. Frontend Architecture

#### Vue Component Hierarchy
```
App.vue
├── Navbar.vue (Global)
├── Toast.vue (Global Notifications)
├── LoadingSpinner.vue (Global Loading)
│
├── Router View
    │
    ├── LandingPage.vue (Public)
    │   └── Hero Section
    │   └── Features Grid
    │   └── CTA Section
    │
    ├── LoginPage.vue (Public)
    │   └── Auth Form
    │
    ├── RegisterPage.vue (Public)
    │   └── Registration Form
    │
    ├── StudentDashboard.vue (Auth: Student)
    │   ├── Test List Component
    │   ├── Results Component
    │   └── Performance Chart
    │
    ├── TestInterface.vue (Auth: Student)
    │   ├── Question Display
    │   ├── Answer Input
    │   ├── Timer Component
    │   └── Proctoring Overlay
    │       └── useProctoring composable
    │           ├── Camera Access
    │           ├── ML Model Loading
    │           ├── Face Detection Loop
    │           └── WebRTC Streaming
    │
    ├── TeacherDashboard.vue (Auth: Teacher)
    │   ├── Test Management
    │   ├── Student Results
    │   ├── CSV Export
    │   └── AI Question Generator
    │       └── OCR Upload Interface
    │
    ├── TestCreation.vue (Auth: Teacher)
    │   ├── Manual Question Entry
    │   ├── AI-Assisted Generation
    │   │   ├── Material Upload (PDF/Image)
    │   │   ├── OCR Processing Status
    │   │   ├── AI Question Preview
    │   │   └── Bulk Import
    │   └── Question Bank Search
    │
    ├── ProctoringMonitor.vue (Auth: Teacher)
    │   ├── Live Student Grid
    │   ├── WebRTC Video Elements
    │   ├── Violation Alerts
    │   └── Student Status Cards
    │
    ├── AdminPanel.vue (Auth: Admin)
    │   ├── User Management
    │   ├── System Statistics
    │   └── AI Service Health
    │
    └── ProfilePage.vue (Auth: Any)
        ├── User Info Editor
        └── Password Change
```

#### State Management (Pinia Stores)
```javascript
// stores/auth.js
{
  user: { id, email, role, name },
  token: 'jwt_token',
  isAuthenticated: boolean,
  actions: { login(), logout(), register(), checkAuth() }
}

// stores/quiz.js
{
  currentTest: { id, title, questions, time_limit },
  answers: Map<questionId, answer>,
  timeRemaining: number,
  isSubmitting: boolean,
  actions: { 
    fetchTest(), 
    saveAnswer(), 
    submitTest(), 
    autoSubmit() 
  }
}

// stores/proctoring.js
{
  violations: [],
  isMonitoring: boolean,
  mlModelsLoaded: boolean,
  connectionStatus: 'connected' | 'disconnected',
  actions: { 
    logViolation(), 
    sendViolation(), 
    initWebRTC() 
  }
}
```

---

### 2. Backend Architecture

#### FastAPI Application Structure
```
backend/
├── app/
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Environment configuration
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py            # Login, register, token refresh
│   │   │   ├── tests.py           # CRUD for tests
│   │   │   ├── questions.py       # Question management
│   │   │   ├── attempts.py        # Test submissions
│   │   │   ├── violations.py      # Proctoring logs
│   │   │   ├── ai_questions.py    # AI generation endpoints
│   │   │   └── teaching_ai.py     # Teaching assistant endpoints
│   │   │
│   │   └── dependencies.py        # Dependency injection
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── test.py
│   │   ├── question.py
│   │   ├── attempt.py
│   │   ├── violation.py
│   │   └── learning_material.py
│   │
│   ├── schemas/                   # Pydantic validation schemas
│   │   ├── auth.py
│   │   ├── test.py
│   │   ├── question.py
│   │   └── ai.py
│   │
│   ├── services/
│   │   ├── auth_service.py        # JWT generation, password hashing
│   │   ├── test_service.py        # Business logic for tests
│   │   ├── streaming_service.py   # WebRTC signaling logic
│   │   ├── ai_question_service.py # Groq question generation
│   │   ├── ocr_service.py         # DeepSeek OCR integration
│   │   └── teaching_ai_service.py # Agentic teaching assistant
│   │
│   ├── database/
│   │   ├── connection.py          # Database session management
│   │   └── migrations/            # Alembic migrations
│   │
│   └── utils/
│       ├── security.py            # Password hashing, token validation
│       └── file_handler.py        # File upload processing
│
├── run.py                         # Granian server startup
└── requirements.txt
```

#### API Endpoint Design

##### Authentication Endpoints
```
POST   /api/auth/register          # User registration
POST   /api/auth/login             # User login (returns JWT)
POST   /api/auth/refresh           # Refresh access token
GET    /api/auth/me                # Get current user info
```

##### Test Management Endpoints
```
GET    /api/tests                  # List all tests (filtered by role)
POST   /api/tests                  # Create new test (teacher only)
GET    /api/tests/{id}             # Get test details
PUT    /api/tests/{id}             # Update test
DELETE /api/tests/{id}             # Delete test
GET    /api/tests/{id}/start       # Start test (creates attempt)
POST   /api/tests/{id}/submit      # Submit test answers
```

##### Question Management Endpoints
```
GET    /api/questions              # List questions (with pagination)
POST   /api/questions              # Create question
GET    /api/questions/{id}         # Get question details
PUT    /api/questions/{id}         # Update question
DELETE /api/questions/{id}         # Delete question
```

##### AI-Powered Endpoints
```
POST   /api/ai/upload-material     # Upload PDF/Image for OCR
       Body: { file: File, subject: string }
       Returns: { material_id, extracted_text, page_count }

POST   /api/ai/generate-questions  # Generate questions from material
       Body: { 
         material_id: string, 
         num_questions: number,
         question_types: ['mcq', 'true_false', 'short_answer'],
         difficulty: 'easy' | 'medium' | 'hard'
       }
       Returns: { questions: [...], generation_time: number }

POST   /api/ai/refine-question     # AI refinement of existing question
       Body: { question_id, feedback: string }
       Returns: { refined_question }

POST   /api/ai/teaching-assist     # Ask teaching AI a question
       Body: { 
         student_id, 
         question: string, 
         context: { test_id?, subject? }
       }
       Returns: { 
         answer, 
         follow_up_questions, 
         related_topics 
       }

POST   /api/ai/explain-answer      # AI explanation of correct answer
       Body: { question_id, student_answer, correct_answer }
       Returns: { explanation, learning_resources }
```

##### Proctoring Endpoints
```
POST   /api/violations             # Log a proctoring violation
GET    /api/violations/{attempt_id} # Get violations for test attempt
```

##### Results & Analytics
```
GET    /api/results/{test_id}      # Get all results for a test
GET    /api/results/student/{id}   # Get student's test history
GET    /api/results/export/{test_id} # Export results as CSV
```

##### WebSocket Events (Socket.IO)
```
Client → Server:
- 'webrtc-offer'        # Student sends WebRTC offer
- 'webrtc-answer'       # Teacher sends WebRTC answer
- 'ice-candidate'       # Exchange ICE candidates
- 'violation'           # Real-time violation alert

Server → Client:
- 'monitoring-started'  # Confirm monitoring session
- 'peer-connected'      # WebRTC peer established
- 'violation-received'  # Acknowledge violation log
- 'test-ended'          # Force end test
```

---

### 3. Database Schema

#### Entity Relationship Diagram
```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │──┐
│ email           │  │
│ password_hash   │  │
│ role            │  │  1:N
│ name            │  │
│ created_at      │  │
└─────────────────┘  │
                     │
         ┌───────────┴─────────────────┬─────────────────────┐
         │                             │                     │
         ▼                             ▼                     ▼
┌─────────────────┐          ┌─────────────────┐   ┌──────────────────┐
│     tests       │          │ test_attempts   │   │learning_materials│
├─────────────────┤          ├─────────────────┤   ├──────────────────┤
│ id (PK)         │──┐       │ id (PK)         │   │ id (PK)          │
│ teacher_id (FK) │  │  1:N  │ test_id (FK)    │──┐│ uploaded_by (FK) │
│ title           │  │       │ student_id (FK) │  ││ title            │
│ subject         │  │       │ score           │  ││ subject          │
│ time_limit      │  │       │ started_at      │  ││ file_path        │
│ passing_score   │  │       │ submitted_at    │  ││ extracted_text   │
│ created_at      │  │       │ status          │  ││ ocr_confidence   │
└─────────────────┘  │       └─────────────────┘  ││ created_at       │
                     │                            │└──────────────────┘
                     │                            │
         ┌───────────┴────────────┐               │
         │                        │               │ 1:N
         ▼                        ▼               ▼
┌─────────────────┐      ┌─────────────────┐  ┌─────────────────┐
│   questions     │      │   violations    │  │ai_gen_questions │
├─────────────────┤      ├─────────────────┤  ├─────────────────┤
│ id (PK)         │──┐   │ id (PK)         │  │ id (PK)         │
│ test_id (FK)    │  │1:N│ attempt_id (FK) │  │ material_id (FK)│
│ question_text   │  │   │ type            │  │ question_id (FK)│
│ question_type   │  │   │ timestamp       │  │ prompt_used     │
│ options (JSON)  │  │   │ severity        │  │ model_version   │
│ correct_answer  │  │   │ description     │  │ generated_at    │
│ points          │  │   └─────────────────┘  └─────────────────┘
│ ai_generated    │  │
└─────────────────┘  │
                     │
                     │ 1:N
                     ▼
            ┌─────────────────┐
            │    answers      │
            ├─────────────────┤
            │ id (PK)         │
            │ attempt_id (FK) │
            │ question_id (FK)│
            │ answer          │
            │ is_correct      │
            │ points_earned   │
            └─────────────────┘
```

#### SQL Schema (Key Tables)

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Tests table
CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(100),
    description TEXT,
    time_limit INTEGER NOT NULL,  -- in minutes
    passing_score DECIMAL(5,2),
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_teacher (teacher_id),
    INDEX idx_published (is_published)
);

-- Questions table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    test_id INTEGER REFERENCES tests(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL CHECK (
        question_type IN ('mcq', 'true_false', 'short_answer')
    ),
    options JSONB,  -- For MCQ: ["A", "B", "C", "D"]
    correct_answer VARCHAR(500) NOT NULL,
    points INTEGER DEFAULT 1,
    ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_test (test_id)
);

-- Test attempts table
CREATE TABLE test_attempts (
    id SERIAL PRIMARY KEY,
    test_id INTEGER REFERENCES tests(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    score DECIMAL(5,2),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,
    status VARCHAR(20) CHECK (
        status IN ('in_progress', 'submitted', 'auto_submitted', 'terminated')
    ),
    violation_count INTEGER DEFAULT 0,
    INDEX idx_student_test (student_id, test_id),
    INDEX idx_status (status)
);

-- Violations table
CREATE TABLE violations (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES test_attempts(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- 'no_face', 'multiple_faces', 'tab_switch', etc.
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_attempt (attempt_id),
    INDEX idx_type (type)
);

-- Learning materials table (for AI question generation)
CREATE TABLE learning_materials (
    id SERIAL PRIMARY KEY,
    uploaded_by INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(100),
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL,  -- 'pdf', 'image', 'docx'
    extracted_text TEXT,
    ocr_confidence DECIMAL(5,2),
    page_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_subject (subject)
);

-- AI generated questions tracking
CREATE TABLE ai_gen_questions (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES learning_materials(id),
    question_id INTEGER REFERENCES questions(id),
    prompt_used TEXT,
    model_version VARCHAR(50),  -- 'llama-3.1-70b-versatile'
    generation_time DECIMAL(5,2),  -- in seconds
    teacher_edited BOOLEAN DEFAULT FALSE,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4. AI Service Integration

#### Groq Question Generation Service

```python
# services/ai_question_service.py
from groq import Groq
from typing import List, Dict

class QuestionGenerationService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-70b-versatile"
    
    async def generate_questions(
        self,
        content: str,
        num_questions: int,
        question_types: List[str],
        difficulty: str,
        subject: str
    ) -> List[Dict]:
        """
        Generate questions using Groq AI with structured output
        """
        system_prompt = f"""You are an expert {subject} teacher. 
        Generate high-quality exam questions from the provided content.
        Ensure questions test understanding, not just memorization.
        Output as JSON array with this structure:
        [
          {{
            "question_text": "...",
            "type": "mcq|true_false|short_answer",
            "options": ["A", "B", "C", "D"],  // for MCQ only
            "correct_answer": "...",
            "explanation": "...",
            "difficulty": "easy|medium|hard"
          }}
        ]
        """
        
        user_prompt = f"""
        Content to generate questions from:
        {content[:4000]}  # Limit token usage
        
        Requirements:
        - Number of questions: {num_questions}
        - Question types: {', '.join(question_types)}
        - Difficulty level: {difficulty}
        - Ensure answers are unambiguous
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
```

#### DeepSeek OCR Service

```python
# services/ocr_service.py
from deepseek import OCRClient
from PIL import Image

class OCRService:
    def __init__(self):
        self.client = OCRClient(api_key=settings.DEEPSEEK_API_KEY)
    
    async def extract_text_from_file(
        self,
        file_path: str,
        file_type: str
    ) -> Dict:
        """
        Extract text using DeepSeek OCR
        """
        if file_type == 'pdf':
            # Process PDF pages
            result = self.client.extract_text(
                file_path=file_path,
                output_format="structured_json",
                include_layout=True
            )
        else:
            # Process image
            result = self.client.extract_text(
                file_path=file_path,
                output_format="structured_json"
            )
        
        return {
            "text": result.text,
            "confidence": result.confidence,
            "layout": result.layout,
            "tables": result.tables,
            "formulas": result.formulas
        }
```

#### Teaching AI Assistant Service

```python
# services/teaching_ai_service.py
class TeachingAssistantService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-70b-versatile"
    
    async def answer_student_query(
        self,
        question: str,
        context: Dict,
        student_history: List[Dict]
    ) -> Dict:
        """
        Agentic AI for personalized teaching assistance
        """
        # Build context from student's learning history
        context_text = self._build_context(context, student_history)
        
        system_prompt = """You are a patient, knowledgeable teaching assistant.
        Explain concepts clearly, provide examples, and adapt to the student's level.
        If a concept is complex, break it into simpler parts.
        Always encourage learning and critical thinking."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context_text}\n\nQuestion: {question}"}
            ],
            temperature=0.6,
            max_tokens=1500
        )
        
        answer = response.choices[0].message.content
        
        # Generate follow-up questions
        follow_ups = await self._generate_follow_ups(question, answer)
        
        return {
            "answer": answer,
            "follow_up_questions": follow_ups,
            "related_topics": self._extract_topics(answer)
        }
```

---

### 5. WebRTC Proctoring Flow

```
Student Device                 Signaling Server              Teacher Dashboard
     │                               │                              │
     │ 1. Start Test                 │                              │
     ├──────────────────────────────>│                              │
     │                               │                              │
     │ 2. Request Camera Access      │                              │
     │    (getUserMedia)             │                              │
     │                               │                              │
     │ 3. Create RTCPeerConnection   │                              │
     │    + DataChannel              │                              │
     │                               │                              │
     │ 4. Create Offer               │                              │
     ├────────'webrtc-offer'────────>│                              │
     │                               │ 5. Forward Offer             │
     │                               ├─────────────────────────────>│
     │                               │                              │
     │                               │ 6. Create Answer             │
     │                               │<─────────────────────────────┤
     │                               │                              │
     │ 7. Receive Answer             │                              │
     │<────'webrtc-answer'───────────┤                              │
     │                               │                              │
     │ 8. Exchange ICE Candidates    │                              │
     │<────────'ice-candidate'───────┼──────────'ice-candidate'────>│
     │                               │                              │
     │ 9. WebRTC Connection Established (P2P Video Stream)          │
     │<──────────────────────────────────────────────────────────────>│
     │                               │                              │
     │ 10. ML Face Detection         │                              │
     │     (Client-Side TensorFlow.js)                              │
     │                               │                              │
     │ 11. Violation Detected        │                              │
     ├─────────'violation'──────────>│                              │
     │                               │ 12. Log & Alert              │
     │                               ├─────────────────────────────>│
     │                               │                              │
     │ 13. Audio Levels via DataChannel                             │
     │────────────────────────────────────────────────────────────────>│
     │                               │                              │
     │ 14. Test Submitted            │                              │
     ├──────────────────────────────>│ 15. Close WebRTC            │
     │                               ├─────────────────────────────>│
     │ 16. Close Connection          │<─────────────────────────────┤
     │<──────────────────────────────┤                              │
```

---

### 6. Data Flow Diagrams

#### Test Creation with AI Flow
```
Teacher
   │
   ├─1─> Upload Learning Material (PDF/Image)
   │      └─> Backend: /api/ai/upload-material
   │           └─> Save file to storage
   │           └─> Call DeepSeek OCR
   │                └─> Extract text, layout, tables
   │                └─> Save to learning_materials table
   │                └─> Return material_id
   │
   ├─2─> Request AI Question Generation
   │      └─> Backend: /api/ai/generate-questions
   │           └─> Retrieve extracted text from DB
   │           └─> Call Groq AI with prompt
   │                └─> Generate questions (JSON)
   │           └─> Save to questions table
   │           └─> Link to ai_gen_questions table
   │           └─> Return generated questions
   │
   ├─3─> Review & Edit Questions (Optional)
   │      └─> Backend: PUT /api/questions/{id}
   │           └─> Update question
   │           └─> Mark as teacher_edited
   │
   └─4─> Publish Test
          └─> Backend: PUT /api/tests/{id}
              └─> Set is_published = true
```

#### Student Test Taking Flow
```
Student
   │
   ├─1─> View Available Tests
   │      └─> Backend: GET /api/tests
   │           └─> Return published tests
   │
   ├─2─> Start Test
   │      └─> Backend: GET /api/tests/{id}/start
   │           └─> Create test_attempt record
   │           └─> Initialize WebSocket connection
   │           └─> Return test questions
   │
   ├─3─> Request Camera Access
   │      └─> Browser: navigator.mediaDevices.getUserMedia()
   │           └─> User grants permission
   │
   ├─4─> Initialize Proctoring
   │      └─> Load ML models (TensorFlow.js)
   │      └─> Start WebRTC stream to teacher
   │      └─> Start face detection loop
   │           └─> Every 1s: Detect faces
   │                └─> If violation: Log & send to backend
   │
   ├─5─> Answer Questions
   │      └─> Auto-save every 30s
   │           └─> Backend: PUT /api/attempts/{id}/answers
   │
   ├─6─> Submit Test
   │      └─> Backend: POST /api/tests/{id}/submit
   │           └─> Calculate score
   │           └─> Update test_attempt
   │           └─> Close WebRTC connection
   │           └─> Return results
   │
   └─7─> View Results
          └─> Backend: GET /api/results/{attempt_id}
              └─> Return score, answers, violations
```

---

### 7. Security Architecture

#### Authentication Flow
```
Client                     Backend                    Database
  │                          │                           │
  │ 1. POST /api/auth/login  │                           │
  ├─────────────────────────>│                           │
  │   {email, password}      │ 2. Query user             │
  │                          ├──────────────────────────>│
  │                          │<──────────────────────────┤
  │                          │ 3. Verify password (bcrypt)│
  │                          │                           │
  │                          │ 4. Generate JWT           │
  │                          │    (RS256 signed)         │
  │                          │    Claims: {id, role, exp}│
  │                          │                           │
  │ 5. Return tokens         │                           │
  │<─────────────────────────┤                           │
  │   {                      │                           │
  │     access_token: '...',  │                           │
  │     refresh_token: '...', │                           │
  │     expires_in: 900      │                           │
  │   }                      │                           │
  │                          │                           │
  │ 6. Subsequent requests   │                           │
  │    (Authorization: Bearer)│                           │
  ├─────────────────────────>│ 7. Verify JWT signature   │
  │                          │ 8. Check expiration       │
  │                          │ 9. Extract user claims    │
  │                          │10. Check role permissions │
  │                          │                           │
  │11. Protected resource    │                           │
  │<─────────────────────────┤                           │
```

#### Data Protection Layers
1. **Transport Layer**: TLS 1.3 for all HTTPS/WSS connections
2. **Application Layer**: JWT token validation, CORS policies
3. **Database Layer**: Encrypted at rest (AES-256), connection pooling
4. **File Storage**: Encrypted uploads, signed URLs for access

---

### 8. Scalability Design

#### Horizontal Scaling Strategy
```
                    Load Balancer (Nginx/HAProxy)
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   FastAPI Instance 1   FastAPI Instance 2   FastAPI Instance 3
   (Granian Server)     (Granian Server)     (Granian Server)
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    Shared PostgreSQL Cluster
                    (Primary + Read Replicas)
```

#### Caching Strategy (Future)
```
Redis Cache Layer
├── Session Data (JWT refresh tokens)
├── Test Questions (Frequently accessed)
├── AI-Generated Content (TTL: 24h)
└── User Profiles (TTL: 1h)
```

---

### 9. Monitoring & Logging

#### Application Logs
```python
# Structured logging format
{
  "timestamp": "2025-10-27T10:30:15Z",
  "level": "INFO",
  "service": "ai_question_service",
  "function": "generate_questions",
  "user_id": 123,
  "message": "Generated 10 questions",
  "metadata": {
    "material_id": 456,
    "generation_time": 1.2,
    "model": "llama-3.1-70b-versatile"
  }
}
```

#### Metrics to Track
- API response times (p50, p95, p99)
- WebRTC connection success rate
- ML model inference time
- Groq API latency and error rate
- Database query performance
- Violation detection accuracy

---

This system design provides a robust, scalable architecture for ProtoLearn's AI-powered proctoring and learning platform.
