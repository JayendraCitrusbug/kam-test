from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.job import Job, JobStatus
from src.application.dto.job_dto import CreateJobRequestDTO, JobResponseDTO
from infrastructure.redis.redis_queue import RedisQueue
from infrastructure.websockets.redis_pubsub import RedisPubSubService
from src.application.dto.websocket_dto import WebsocketMessageTypesEnum


class JobSchedulerService:
    def __init__(self, db: AsyncSession, queue: RedisQueue):
        self.db = db
        self.queue = queue
        self.pubsub = RedisPubSubService()

    async def _publish_job_status(self, job: Job, status: str, message: str):
        """
        Publishes the status of a job to connected websocket clients.

        Args:
            job (Job): The job to publish the status of.
            status (str): The status of the job, e.g. "scheduled", "in_progress", "completed", "failed", or "cancelled".
            message (str): The message to include with the job status update.

        Returns:
            None
        """
        await self.pubsub.publish_updates(
            data_type=WebsocketMessageTypesEnum.job_status,
            data={
                "job_id": job.id,
                "status": status,
                "message": message,
                "job_details": {
                    "id": job.id,
                    "job_name": job.job_name,
                    "phone_number": job.phone_number,
                    "status": (
                        job.status.value
                        if hasattr(job.status, "value")
                        else str(job.status)
                    ),
                    "schedule_time": job.schedule_time.isoformat(),
                    "created_at": job.created_at.isoformat(),
                    "updated_at": job.updated_at.isoformat(),
                },
            },
        )

    async def schedule_job(self, job_data: CreateJobRequestDTO) -> JobResponseDTO:
        """
        Schedules a new job by storing it in the database, publishing its initial status,
        and adding it to the processing queue.

        Args:
            job_data (CreateJobRequestDTO): The data required to create a new job,
            including job name, phone number, and schedule time.

        Returns:
            JobResponseDTO: A data transfer object containing the details of the scheduled job.

        Raises:
            Exception: If an error occurs during the job scheduling process,
            the transaction is rolled back and the exception is raised.
        """

        try:
            job = Job(
                id=str(uuid4()),
                job_name=job_data.job_name,
                phone_number=job_data.phone_number,
                status=JobStatus.SCHEDULED.value,
                schedule_time=job_data.schedule_time,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)

            # Publish initial status
            await self._publish_job_status(
                job=job,
                status="scheduled",
                message=f"Twilio Job {job.job_name} scheduled for {job.schedule_time}",
            )

            # Add to processing queue
            await self.queue.enqueue(
                {
                    "id": job.id,
                    "job_name": job.job_name,
                    "schedule_time": job.schedule_time.isoformat(),
                }
            )

            return JobResponseDTO(
                id=job.id,
                job_name=job.job_name,
                phone_number=job.phone_number,
                status=job.status,
                schedule_time=job.schedule_time,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
        except Exception as e:
            await self.db.rollback()
            raise e
