"""统一异常与错误响应模块。

目标：
1. 业务异常使用稳定的字符串错误码，前端可据此做精细化处理。
2. 所有异常返回统一 JSON 结构：{"code": ..., "message": ..., "details": ...}。
3. 不把生产环境的堆栈信息暴露给客户端，但会完整写入服务端日志。
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """可预期的业务异常基类。

    参数：
    - status_code: HTTP 状态码
    - code: 稳定的业务错误码，例如 STOCK_NOT_FOUND
    - message: 面向用户的中文错误说明
    - details: 可选的补充信息，必须是 JSON 可序列化对象
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class NotFoundError(AppException):
    """资源不存在异常。"""

    def __init__(self, code: str, message: str, details: Any | None = None) -> None:
        super().__init__(status_code=404, code=code, message=message, details=details)


class DataProviderError(AppException):
    """外部数据源异常。

    该异常用于包装 AKShare 等第三方接口的超时、限流、字段变化等问题，
    避免底层异常直接泄漏到 API 层。
    """

    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(
            status_code=502,
            code="MARKET_DATA_PROVIDER_ERROR",
            message=message,
            details=details,
        )


def _error_payload(code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    """构造统一错误响应体。"""
    return {"code": code, "message": message, "details": details}


async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """处理业务异常。"""
    logger.warning("业务异常 code=%s message=%s details=%s", exc.code, exc.message, exc.details)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(exc.code, exc.message, exc.details),
    )


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """处理 FastAPI/Starlette 内置 HTTPException。

    兼容 detail 为字符串、字典或列表的情况，统一包装为错误码结构。
    """
    if isinstance(exc.detail, str):
        message = exc.detail
        details = None
    else:
        message = "请求处理失败"
        details = exc.detail

    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(f"HTTP_{exc.status_code}", message, details),
        headers=exc.headers,
    )


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """处理请求参数校验失败（默认 HTTP 422）。"""
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            code="VALIDATION_ERROR",
            message="请求参数校验失败，请检查输入内容",
            details=jsonable_encoder(exc.errors()),
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底处理未预期异常。

    调试模式返回异常摘要，生产环境只返回通用提示；完整堆栈写入日志。
    """
    logger.exception("未处理异常 path=%s method=%s", request.url.path, request.method)
    return JSONResponse(
        status_code=500,
        content=_error_payload(
            code="INTERNAL_SERVER_ERROR",
            message="服务内部错误，请稍后重试",
            details=str(exc) if settings.debug else None,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """把全部异常处理器注册到 FastAPI 应用。"""
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
