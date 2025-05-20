from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class WebsocketMessageTypesEnum(str, Enum):
    job_status = "job_status"


class JobStatusUpdateDTO(BaseModel):
    job_id: str
    status: str
    updated_at: datetime
