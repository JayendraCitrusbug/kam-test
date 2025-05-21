from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from src.application.dto.job_dto import CreateJobRequestDTO, JobResponseDTO
from src.application.services.job_scheduler import JobSchedulerService
from infrastructure.redis.redis_queue import RedisQueue
from src.domain.models.job import Job
from infrastructure.database.db import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponseDTO, status_code=status.HTTP_201_CREATED)
async def schedule_job(
    job_request: CreateJobRequestDTO,
    db: Session = Depends(get_db),
):
    """
    Schedule a new job by storing it in the database, publishing its initial status,
    and adding it to the processing queue.

    Args:
        job_request (CreateJobRequestDTO): The data required to create a new job,
            including job name, phone number, and schedule time.

    Returns:
        JobResponseDTO: A data transfer object containing the details of the scheduled job.

    Raises:
        HTTPException: If an error occurs during the job scheduling process,
            the transaction is rolled back and the exception is raised.
    """
    # Validate schedule_time is in the future
    if job_request.schedule_time <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="schedule_time must be in the future",
        )

    queue = RedisQueue()
    service = JobSchedulerService(db, queue)
    job_response = await service.schedule_job(job_request)
    await queue.close()
    return job_response
