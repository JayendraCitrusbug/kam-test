from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class JobStatusEnum(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobCreate(BaseModel):
    job_name: str
    job_type: str


class JobUpdateStatus(BaseModel):
    status: JobStatusEnum
