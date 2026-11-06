"""通用响应结构。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PageResponse[T](BaseModel):
    """分页响应。

    items 每页数据，total 总记录数，pages 总页数，便于前端直接渲染分页器。
    """

    items: list[T] = Field(default_factory=list, description="当前页数据")
    total: int = Field(ge=0, description="总记录数")
    page: int = Field(ge=1, description="当前页码")
    page_size: int = Field(ge=1, description="每页数量")
    pages: int = Field(ge=0, description="总页数")


class ErrorResponse(BaseModel):
    """统一错误响应结构，仅用于 OpenAPI 文档展示。"""

    code: str = Field(description="稳定错误码")
    message: str = Field(description="用户可读的错误说明")
    details: object | None = Field(default=None, description="可选的详细错误信息")


class MessageResponse(BaseModel):
    """简单消息响应。"""

    message: str
