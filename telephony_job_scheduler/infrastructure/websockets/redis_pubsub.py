import asyncio
import json
import logging
from typing import Any, Dict

from redis.asyncio import Redis

from config.settings import app_settings
from infrastructure.websockets.connection_manager import ConnectionManager
from src.application.dto.websocket_dto import WebsocketMessageTypesEnum

logger = logging.getLogger(__name__)


class RedisPubSubService:
    def __init__(self):
        self.redis_conn = Redis(
            host=app_settings.REDIS_HOST,
            port=app_settings.REDIS_PORT,
            decode_responses=True,
        )
        self.channel = "public_channel"

    async def redis_listener(self):
        """
        Listens for Redis messages on the configured channel and broadcasts
        received messages to all active WebSocket connections.

        This method is intended to be run in a separate task as it runs an
        infinite loop. If the listener is stopped for any reason, it will
        attempt to reconnect and resume broadcasting messages.

        :raises: Any exceptions raised during the execution of this method
        """
        pubsub = self.redis_conn.pubsub()
        await pubsub.subscribe(self.channel)

        connection_manager = ConnectionManager()

        try:
            while True:
                try:
                    message = await asyncio.wait_for(
                        pubsub.get_message(ignore_subscribe_messages=True), timeout=1.0
                    )
                    if not message:
                        await asyncio.sleep(0.1)
                        continue

                    if message["type"] != "message":
                        continue

                    try:
                        data = json.loads(message["data"])
                    except json.JSONDecodeError as e:
                        logger.error(
                            "Invalid JSON on channel %s: %s", self.channel, str(e)
                        )
                        continue

                    logger.debug("Broadcasting on %s: %s", self.channel, data)
                    await connection_manager.broadcast(data)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.exception("Error processing Redis message: %s", str(e))
                    await asyncio.sleep(1)

        except Exception as e:
            logger.exception("Redis listener error: %s", str(e))
        finally:
            await pubsub.unsubscribe()
            await pubsub.close()

    async def publish_updates(
        self,
        data_type: WebsocketMessageTypesEnum,
        data: Dict[str, Any],
    ):
        """
        Publishes updates to a Redis channel with the specified data type and data.

        This method serializes the given data into JSON format, using a custom
        serializer for handling enum values and datetime objects, and publishes
        it to the Redis channel.

        Args:
            data_type (WebsocketMessageTypesEnum): The type of message being
                published, corresponding to an enum value that identifies the
                message category.
            data (Dict[str, Any]): The data payload to be included in the message,
                which will be serialized to JSON.

        Raises:
            TypeError: If an object within the data is not JSON serializable.
            Exception: If there is an error during the publishing of the message,
                which is logged with an exception message.
        """

        def default_serializer(obj):
            if hasattr(obj, "value"):  # For enum values
                return obj.value
            elif hasattr(obj, "isoformat"):  # For datetime
                return obj.isoformat()
            raise TypeError(
                f"Object of type {type(obj).__name__} is not JSON serializable"
            )

        try:
            message = json.dumps({data_type.value: data}, default=default_serializer)
            await self.redis_conn.publish(self.channel, message)
        except Exception as e:
            logger.exception("Error publishing Redis message: %s", str(e))
