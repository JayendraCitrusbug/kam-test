from redis.asyncio import Redis
from config.settings import app_settings


def get_redis_client() -> Redis:
    return Redis(
        host=app_settings.REDIS_HOST,
        port=app_settings.REDIS_PORT,
        db=app_settings.REDIS_DB,
        decode_responses=True,
    )
