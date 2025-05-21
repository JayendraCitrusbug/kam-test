import time
import logging
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Log request and response details including method, URL path, status code,
        and duration of request processing.

        Args:
            request (Request): The incoming HTTP request.
            call_next (function): The function to call to get the response.

        Returns:
            Response: The HTTP response after processing the request.
        """

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        timestamp = datetime.utcnow().isoformat()

        logger.info(
            f"[{timestamp}] {request.method} {request.url.path} - "
            f"{response.status_code} - {duration:.4f}s"
        )

        return response
