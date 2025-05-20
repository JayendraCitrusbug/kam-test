from infrastructure.websockets.redis_pubsub import RedisPubSubService
from src.application.dto.websocket_dto import WebsocketMessageTypesEnum

redis_service = RedisPubSubService()


async def publish_job_status(job):
    await redis_service.publish_updates(
        data_type=WebsocketMessageTypesEnum.job_status, data=job.to_dict()
    )
