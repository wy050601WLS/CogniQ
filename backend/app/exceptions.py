"""统一异常体系"""
from fastapi import HTTPException


class AppException(HTTPException):
    """应用基础异常"""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        detail: dict = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.detail = detail or {}


class NotFoundError(AppException):
    """资源不存在"""

    def __init__(self, resource: str = "资源", resource_id: str = ""):
        msg = f"{resource}不存在" if not resource_id else f"{resource} '{resource_id}' 不存在"
        super().__init__(status_code=404, code="NOT_FOUND", message=msg)


class ValidationError(AppException):
    """数据验证错误"""

    def __init__(self, message: str = "数据验证失败"):
        super().__init__(status_code=422, code="VALIDATION_ERROR", message=message)


class ProcessingError(AppException):
    """处理错误"""

    def __init__(self, message: str = "处理失败"):
        super().__init__(status_code=500, code="PROCESSING_ERROR", message=message)


class ExternalServiceError(AppException):
    """外部服务错误"""

    def __init__(self, service: str, message: str = "服务不可用"):
        super().__init__(status_code=503, code="EXTERNAL_SERVICE_ERROR", message=f"{service}: {message}")


class PermissionDeniedError(AppException):
    """权限不足"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(status_code=403, code="PERMISSION_DENIED", message=message)


class UnauthorizedError(AppException):
    """未授权"""

    def __init__(self, message: str = "未授权"):
        super().__init__(status_code=401, code="UNAUTHORIZED", message=message)


class BadRequestError(AppException):
    """请求错误"""

    def __init__(self, message: str = "请求错误"):
        super().__init__(status_code=400, code="BAD_REQUEST", message=message)
