import asyncio
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from config.logging import setup_logging
from config.settings import app_settings
from infrastructure.database.db import Base, engine, get_db
from infrastructure.redis.redis_queue import RedisQueue
from infrastructure.websockets.redis_pubsub import RedisPubSubService
from src.application.services.job_scheduler import JobSchedulerService
from src.application.services.job_worker import JobWorkerService
from src.routers import jobs, websocket

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=app_settings.APP_NAME,
    description="Telephony Job Scheduler Service API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(websocket.router)


@app.on_event("startup")
async def startup_event():
    # Create DB tables
    """
    Called on application startup.

    Performs the following tasks:

    1. Creates all database tables.
    2. Starts the Redis listener.
    3. Starts the job worker.
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start Redis listener
    redis_pubsub = RedisPubSubService()
    asyncio.create_task(redis_pubsub.redis_listener())

    # Start job worker
    async def run_worker():
        queue = RedisQueue()
        async for db in get_db():
            worker = JobWorkerService(db, queue)
            await worker.run()

    asyncio.create_task(run_worker())


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown.")


# Dependency for JobSchedulerService
async def get_job_scheduler_service(db: AsyncSession = Depends(get_db)):
    """
    Dependency to get an instance of JobSchedulerService.

    This dependency will be used in path operations that require an instance of JobSchedulerService.
    It creates a RedisQueue instance and returns an instance of JobSchedulerService with the current database session
    and the RedisQueue instance.

    Args:
        db (AsyncSession): The current database session. Defaults to Depends(get_db).

    Returns:
        JobSchedulerService: An instance of JobSchedulerService.
    """
    queue = RedisQueue()
    return JobSchedulerService(db, queue)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
