from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Enum, DateTime
from infrastructure.database.db import Base


class JobStatus(PyEnum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    job_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.SCHEDULED.value)
    schedule_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Job(id={self.id}, job_name={self.job_name}, status={self.status})>"

    def to_dict(self):
        return {
            "id": self.id,
            "job_name": self.job_name,
            "phone_number": self.phone_number,
            "status": self.status.value,
            "schedule_time": self.schedule_time.isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
