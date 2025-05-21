from infrastructure.websockets.redis_pubsub import RedisPubSubService
from src.application.dto.websocket_dto import WebsocketMessageTypesEnum

redis_service = RedisPubSubService()


async def publish_job_status(job):
    """
    Publishes the given Job to the Redis channel as a JSON payload.

    Args:
        job (Job): The Job object to be published.

    Raises:
        TypeError: If an object within the Job is not JSON serializable.
        Exception: If there is an error during the publishing of the message,
            which is logged with an exception message.
    """
    await redis_service.publish_updates(
        data_type=WebsocketMessageTypesEnum.job_status, data=job.to_dict()
    )
