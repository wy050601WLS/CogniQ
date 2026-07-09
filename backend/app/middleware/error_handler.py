"""全局异常处理中间件"""
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.exceptions import AppException

logger = logging.getLogger("app.error")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except AppException as e:
            logger.warning(f"AppException: {e.code} - {e.message}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "code": e.code,
                        "message": e.message,
                        "detail": e.detail,
                    }
                },
            )
        except Exception as e:
            # 记录详细的错误信息
            error_trace = traceback.format_exc()
            logger.error(f"Unhandled exception: {type(e).__name__}: {e}")
            logger.error(f"Traceback:\n{error_trace}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "服务器内部错误，请稍后重试",
                    }
                },
            )
