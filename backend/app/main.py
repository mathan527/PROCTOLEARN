from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api import auth, tests, questions, ai, proctoring, queue, ai_materials
from app.services.streaming_service import streaming_manager
from app.services.queue_service import queue_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting ProctoLearn...")
    await init_db()
    print("Database initialized")
    
    settings.UPLOAD_DIR.mkdir(exist_ok=True)
    settings.PROCTORING_LOGS_DIR.mkdir(exist_ok=True)
    print("Upload directories created")
    
    await streaming_manager.setup_handlers()
    print("WebSocket handlers initialized")
    
    await queue_service.connect()
    print("Queue service connected")
    
    yield
    
    print("Shutting down...")
    await queue_service.disconnect()
    await close_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Granian compatibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

if settings.UPLOAD_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(tests.router, prefix=f"{settings.API_V1_STR}/tests", tags=["Tests"])
app.include_router(questions.router, prefix=f"{settings.API_V1_STR}/questions", tags=["Questions"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}/ai", tags=["AI"])
app.include_router(ai_materials.router, prefix=f"{settings.API_V1_STR}/ai-materials", tags=["AI Materials"])
app.include_router(proctoring.router, prefix=f"{settings.API_V1_STR}/proctoring", tags=["Proctoring"])
app.include_router(queue.router, prefix=f"{settings.API_V1_STR}/queue", tags=["Queue"])

socket_app = streaming_manager.get_asgi_app()
app.mount("/socket.io", socket_app)

@app.get("/")
async def root():
    return {
        "message": "🎓 ProctoLearn API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
