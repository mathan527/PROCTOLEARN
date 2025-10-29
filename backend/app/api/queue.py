"""
API endpoints for checking queue status and system load
"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models import User
from app.services.queue_service import queue_service

router = APIRouter()

@router.get("/status")
async def get_queue_status(user: User = Depends(get_current_user)):
    """Get current queue status and system load"""
    
    ai_queue_length = await queue_service.get_queue_length(queue_service.AI_GENERATION_QUEUE)
    test_queue_length = await queue_service.get_queue_length(queue_service.TEST_PROCESSING_QUEUE)
    proctoring_queue_length = await queue_service.get_queue_length(queue_service.PROCTORING_QUEUE)
    
    ai_active = await queue_service.get_active_count(queue_service.AI_GENERATION_QUEUE)
    test_active = await queue_service.get_active_count(queue_service.TEST_PROCESSING_QUEUE)
    proctoring_active = await queue_service.get_active_count(queue_service.PROCTORING_QUEUE)
    
    return {
        "queues": {
            "ai_generation": {
                "queued": ai_queue_length,
                "processing": ai_active,
                "capacity": queue_service.MAX_CONCURRENT_AI_TASKS,
                "available_slots": max(0, queue_service.MAX_CONCURRENT_AI_TASKS - ai_active)
            },
            "test_processing": {
                "queued": test_queue_length,
                "processing": test_active,
                "capacity": queue_service.MAX_CONCURRENT_TEST_TASKS,
                "available_slots": max(0, queue_service.MAX_CONCURRENT_TEST_TASKS - test_active)
            },
            "proctoring": {
                "queued": proctoring_queue_length,
                "processing": proctoring_active,
                "capacity": queue_service.MAX_CONCURRENT_PROCTORING,
                "available_slots": max(0, queue_service.MAX_CONCURRENT_PROCTORING - proctoring_active)
            }
        },
        "system_status": "operational" if ai_active < queue_service.MAX_CONCURRENT_AI_TASKS else "busy"
    }

@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    user: User = Depends(get_current_user)
):
    """Get status of a specific task"""
    task = await queue_service.get_task_status(task_id)
    
    if not task:
        return {"status": "not_found"}
    
    return task
