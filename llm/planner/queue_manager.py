import asyncio
from typing import Dict, List
from collections import deque
from datetime import datetime
from .models import DecideResponse, StepType


class TaskQueue:
    """Queue for managing tasks within a single session."""
    
    def __init__(self):
        self.queue = deque()
        self.processing = []
        self.completed = []
        self.lock = asyncio.Lock()
    
    def add_task(self, task: dict):
        """Add a task to the queue."""
        task['status'] = 'pending'
        task['queued_at'] = datetime.now().isoformat()
        self.queue.append(task)
    
    def get_status(self) -> dict:
        """Get current queue status."""
        return {
            'pending': list(self.queue),
            'processing': self.processing.copy(),
            'completed': self.completed.copy()
        }


class QueueManager:
    """Manages task queues for all sessions."""
    
    def __init__(self):
        self.session_queues: Dict[str, TaskQueue] = {}
        self._lock = asyncio.Lock()
    
    async def get_or_create_queue(self, sid: str) -> TaskQueue:
        """Get or create a queue for the session."""
        async with self._lock:
            if sid not in self.session_queues:
                self.session_queues[sid] = TaskQueue()
            return self.session_queues[sid]
    
    async def enqueue_tasks(self, sid: str, tasks: List[dict]):
        """Add multiple tasks to session queue."""
        queue = await self.get_or_create_queue(sid)
        async with queue.lock:
            for task in tasks:
                queue.add_task(task)
    
    async def process_next_task(self, sid: str, processor_func) -> DecideResponse:
        """Process the next task in queue sequentially."""
        queue = await self.get_or_create_queue(sid)
        
        async with queue.lock:
            if not queue.queue:
                return None
            
            task = queue.queue.popleft()
            task['status'] = 'processing'
            task['started_at'] = datetime.now().isoformat()
            queue.processing.append(task)
        
        # Process outside the lock to allow other operations
        result = await processor_func(task)
        
        async with queue.lock:
            queue.processing.remove(task)
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            queue.completed.append(task)
        
        return result
    
    async def process_all_tasks(self, sid: str, processor_func) -> List[DecideResponse]:
        """Process all tasks in queue sequentially."""
        results = []
        queue = await self.get_or_create_queue(sid)
        
        # Get count of tasks to process
        async with queue.lock:
            task_count = len(queue.queue)
        
        # Process each task sequentially
        for _ in range(task_count):
            result = await self.process_next_task(sid, processor_func)
            if result:
                results.append(result)
        
        return results
    
    async def get_queue_status(self, sid: str) -> dict:
        """Get status of session queue."""
        queue = await self.get_or_create_queue(sid)
        async with queue.lock:
            return queue.get_status()


# Global queue manager instance
_queue_manager = None

def get_queue_manager() -> QueueManager:
    """Get or create global queue manager instance."""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = QueueManager()
    return _queue_manager


