import json
from redis.asyncio import Redis
from config.settings import app_settings


class RedisQueue:
    def __init__(self, queue_name: str = "job_queue"):
        self.queue_name = queue_name
        self.redis = Redis(host=app_settings.REDIS_HOST, decode_responses=True)

    async def enqueue(self, job_data: dict) -> None:
        await self.redis.rpush(self.queue_name, json.dumps(job_data))

    async def dequeue(self) -> dict | None:
        job_json = await self.redis.lpop(self.queue_name)
        return json.loads(job_json) if job_json else None

    async def size(self) -> int:
        return await self.redis.llen(self.queue_name)

    async def close(self):
        await self.redis.close()
