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
    print("job req -- ", job_request)
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
