"""请求日志中间件"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("app.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    """记录请求日志"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = (time.time() - start_time) * 1000
        status = response.status_code
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""

        log_msg = f"{method} {path}"
        if query:
            log_msg += f"?{query}"
        log_msg += f" -> {status} ({duration:.0f}ms)"

        if status >= 500:
            logger.error(log_msg)
        elif status >= 400:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return response
