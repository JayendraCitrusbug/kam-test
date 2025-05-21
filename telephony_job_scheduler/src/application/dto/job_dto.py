from datetime import datetime

from pydantic import BaseModel, Field


class CreateJobRequestDTO(BaseModel):
    job_name: str = Field(..., example="Twilio Job")
    phone_number: str = Field(..., example="+1234567890")
    schedule_time: datetime = Field(..., example="2025-05-20 12:00")


class JobResponseDTO(BaseModel):
    id: str
    job_name: str
    phone_number: str
    status: str
    schedule_time: datetime
    created_at: datetime
    updated_at: datetime
