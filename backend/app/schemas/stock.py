"""股票相关 API 数据契约。"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class StockRead(BaseModel):
    """股票详情/列表项。

    from_attributes=True 让 Pydantic 可以直接读取 SQLAlchemy ORM 对象。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str = Field(description="6 位证券代码")
    name: str = Field(description="证券简称")
    exchange: str = Field(description="交易所代码：SSE/SZSE/BSE")
    market: str = Field(description="板块：主板/创业板/科创板/北交所")
    industry: str | None = Field(default=None, description="所属行业")
    list_date: date | None = Field(default=None, description="上市日期")
    is_active: bool = Field(description="是否正常上市")
    data_source: str = Field(description="数据来源，demo 表示演示数据")
    description: str | None = Field(default=None, description="备注说明")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class SelectOption(BaseModel):
    """筛选下拉框选项。"""

    value: str = Field(description="选项值")
    label: str = Field(description="中文展示名称")


class StockFilterOptions(BaseModel):
    """股票池筛选项。

    后端从数据库实时聚合，避免前端硬编码交易所/行业后与数据不一致。
    """

    exchanges: list[SelectOption] = Field(default_factory=list, description="交易所选项")
    industries: list[str] = Field(default_factory=list, description="行业列表")
