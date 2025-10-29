"""
Queue Service for managing concurrent AI operations
Uses Redis for task queuing to prevent resource exhaustion
"""
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import redis.asyncio as redis
from app.core.config import settings

class QueueService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.processing_lock = asyncio.Lock()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        
        # Queue names
        self.AI_GENERATION_QUEUE = "queue:ai_generation"
        self.TEST_PROCESSING_QUEUE = "queue:test_processing"
        self.PROCTORING_QUEUE = "queue:proctoring"
        
        # Limits
        self.MAX_CONCURRENT_AI_TASKS = 3
        self.MAX_CONCURRENT_TEST_TASKS = 10
        self.MAX_CONCURRENT_PROCTORING = 50
        
    async def connect(self):
        """Connect to Redis"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def enqueue(self, queue_name: str, task_data: Dict[str, Any], priority: int = 0) -> str:
        """
        Add a task to the queue
        
        Args:
            queue_name: Name of the queue
            task_data: Task data to enqueue
            priority: Task priority (higher = more important)
        
        Returns:
            task_id: Unique task identifier
        """
        await self.connect()
        
        task_id = f"{queue_name}:{datetime.utcnow().timestamp()}"
        task = {
            "id": task_id,
            "data": task_data,
            "priority": priority,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "attempts": 0
        }
        
        # Add to Redis sorted set (sorted by priority)
        await self.redis_client.zadd(
            queue_name,
            {json.dumps(task): priority}
        )
        
        # Store task metadata
        await self.redis_client.setex(
            f"task:{task_id}",
            3600,  # Expire in 1 hour
            json.dumps(task)
        )
        
        return task_id
    
    async def dequeue(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the highest priority task from queue
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            Task data or None if queue is empty
        """
        await self.connect()
        
        # Get highest priority item (ZREVRANGE for descending order)
        result = await self.redis_client.zrevrange(queue_name, 0, 0)
        
        if not result:
            return None
        
        task_json = result[0]
        task = json.loads(task_json)
        
        # Remove from queue
        await self.redis_client.zrem(queue_name, task_json)
        
        # Update task status
        task["status"] = "processing"
        await self.redis_client.setex(
            f"task:{task['id']}",
            3600,
            json.dumps(task)
        )
        
        return task
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        await self.connect()
        
        task_json = await self.redis_client.get(f"task:{task_id}")
        if task_json:
            return json.loads(task_json)
        return None
    
    async def update_task_status(self, task_id: str, status: str, result: Any = None):
        """Update task status"""
        await self.connect()
        
        task_json = await self.redis_client.get(f"task:{task_id}")
        if task_json:
            task = json.loads(task_json)
            task["status"] = status
            task["updated_at"] = datetime.utcnow().isoformat()
            
            if result:
                task["result"] = result
            
            if status == "failed":
                task["attempts"] += 1
            
            await self.redis_client.setex(
                f"task:{task_id}",
                3600,
                json.dumps(task)
            )
    
    async def get_queue_length(self, queue_name: str) -> int:
        """Get number of tasks in queue"""
        await self.connect()
        return await self.redis_client.zcard(queue_name)
    
    async def get_active_count(self, task_type: str) -> int:
        """Get number of active tasks of a specific type"""
        await self.connect()
        
        # Get all processing tasks
        keys = await self.redis_client.keys(f"task:{task_type}:*")
        processing_count = 0
        
        for key in keys:
            task_json = await self.redis_client.get(key)
            if task_json:
                task = json.loads(task_json)
                if task.get("status") == "processing":
                    processing_count += 1
        
        return processing_count
    
    async def can_process(self, queue_name: str) -> bool:
        """Check if we can process more tasks for this queue"""
        await self.connect()
        
        active_count = await self.get_active_count(queue_name)
        
        if queue_name == self.AI_GENERATION_QUEUE:
            return active_count < self.MAX_CONCURRENT_AI_TASKS
        elif queue_name == self.TEST_PROCESSING_QUEUE:
            return active_count < self.MAX_CONCURRENT_TEST_TASKS
        elif queue_name == self.PROCTORING_QUEUE:
            return active_count < self.MAX_CONCURRENT_PROCTORING
        
        return True
    
    async def process_queue(self, queue_name: str, processor_func):
        """
        Process tasks from queue
        
        Args:
            queue_name: Name of the queue to process
            processor_func: Async function to process each task
        """
        await self.connect()
        
        while True:
            try:
                # Check if we can process more tasks
                if not await self.can_process(queue_name):
                    await asyncio.sleep(1)
                    continue
                
                # Get next task
                task = await self.dequeue(queue_name)
                
                if not task:
                    await asyncio.sleep(1)
                    continue
                
                # Process task
                try:
                    result = await processor_func(task["data"])
                    await self.update_task_status(task["id"], "completed", result)
                except Exception as e:
                    await self.update_task_status(task["id"], "failed", str(e))
                    
                    # Retry if attempts < 3
                    if task["attempts"] < 3:
                        await self.enqueue(
                            queue_name,
                            task["data"],
                            task["priority"] - 1  # Lower priority for retries
                        )
            
            except Exception as e:
                print(f"Queue processing error: {e}")
                await asyncio.sleep(5)

# Global queue service instance
queue_service = QueueService()
