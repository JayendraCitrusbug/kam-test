import asyncio
from datetime import datetime
from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.redis.redis_queue import RedisQueue
from infrastructure.websockets.redis_pubsub import RedisPubSubService
from src.domain.models.job import Job, JobStatus
from src.application.dto.websocket_dto import WebsocketMessageTypesEnum


class JobWorkerService:
    def __init__(self, db: AsyncSession, queue: RedisQueue):
        self.db = db
        self.queue = queue
        self.pubsub = RedisPubSubService()
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.completed_jobs: List[str] = []
        self.failed_jobs: Dict[str, int] = {}

    async def _publish_status(self, message: dict):
        await self.pubsub.publish_updates(
            data_type=WebsocketMessageTypesEnum.job_status, data=message
        )

    async def _update_job_status(self, job_id: str, status: str):
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = result.scalars().first()

        if job:
            job.status = status
            job.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(job)
            return job
        return None

    async def _process_job(self, job_data: dict):
        job_id = job_data["id"]
        try:
            result = await self.db.execute(select(Job).where(Job.id == job_id))
            job = result.scalars().first()

            if not job:
                self.failed_jobs.pop(job_id, None)
                return

            now = datetime.utcnow()
            delay = (job.schedule_time - now).total_seconds()

            if delay > 0:
                await asyncio.sleep(delay)

            # Update status to processing
            job = await self._update_job_status(job.id, JobStatus.IN_PROGRESS.value)
            await self._publish_status(
                {
                    "job_id": job.id,
                    "status": "processing",
                    "message": f"Processing Twilio Job {job.job_name}...",
                    "job_details": {
                        "id": job.id,
                        "job_name": job.job_name,
                        "status": job.status,
                        "schedule_time": job.schedule_time.isoformat(),
                    },
                }
            )

            # Simulate work - replace with actual job processing
            await asyncio.sleep(3)

            # Update status to completed
            job = await self._update_job_status(job.id, JobStatus.COMPLETED.value)
            await self._publish_status(
                {
                    "job_id": job.id,
                    "status": "completed",
                    "message": f"Twilio Job {job.job_name} completed successfully",
                    "job_details": {
                        "id": job.id,
                        "job_name": job.job_name,
                        "status": job.status,
                        "schedule_time": job.schedule_time.isoformat(),
                    },
                }
            )

            # Mark job as completed
            self.completed_jobs.append(job_id)
            if job_id in self.failed_jobs:
                del self.failed_jobs[job_id]

        except Exception as e:
            retry_count = self.failed_jobs.get(job_id, 0) + 1

            if retry_count < 3:  # Max 3 retries
                self.failed_jobs[job_id] = retry_count
                await self.queue.enqueue(job_data)  # Requeue for retry
                await self._publish_status(
                    {
                        "job_id": job_id,
                        "status": "failed",
                        "message": f"Twilio Job failed (attempt {retry_count}/3). Retrying...",
                        "job_details": {
                            "id": job_id,
                            "status": "failed",
                            "retry_count": retry_count,
                        },
                    }
                )
            else:
                await self._update_job_status(job_id, JobStatus.FAILED.value)
                await self._publish_status(
                    {
                        "job_id": job_id,
                        "status": "failed",
                        "message": "Twilio Job failed after 3 attempts. Giving up.",
                        "job_details": {
                            "id": job_id,
                            "status": "failed",
                            "retry_count": retry_count,
                        },
                    }
                )
        finally:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

    async def _monitor_active_jobs(self):
        """Periodically check for stuck jobs and requeue them if needed"""
        while True:
            await asyncio.sleep(60)  # Check every minute
            for job_id, task in list(self.active_jobs.items()):
                if task.done():
                    if task.exception():
                        print(f"Job {job_id} failed: {task.exception()}")
                        # Handle the failed job (could requeue it)
                    del self.active_jobs[job_id]

    async def run(self):
        # Start the monitoring task
        monitor_task = asyncio.create_task(self._monitor_active_jobs())

        try:
            while True:
                job_data = await self.queue.dequeue()
                if not job_data:
                    await asyncio.sleep(1)
                    continue

                job_id = job_data["id"]

                # Skip if already completed or being processed
                if job_id in self.completed_jobs or job_id in self.active_jobs:
                    continue

                # Process the job in a separate task
                task = asyncio.create_task(self._process_job(job_data))
                self.active_jobs[job_id] = task

        except asyncio.CancelledError:
            # Handle graceful shutdown
            await self._cancel_active_jobs()
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        except Exception as e:
            raise

    async def _cancel_active_jobs(self):
        """Cancel all active jobs and requeue them"""
        for job_id, task in self.active_jobs.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    # Requeue the job
                    result = await self.db.execute(select(Job).where(Job.id == job_id))
                    job = result.scalars().first()
                    if job and job.status != JobStatus.COMPLETED.value:
                        await self.queue.enqueue({"id": job_id})
