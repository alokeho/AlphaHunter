"""系统状态与仪表盘数据契约。"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: Literal["ok", "degraded"] = Field(description="服务状态")
    service: str = Field(description="服务名称")
    version: str = Field(description="服务版本")
    environment: str = Field(description="运行环境")
    phase: str = Field(description="当前研发阶段")
    database: Literal["ok", "unavailable"] = Field(description="数据库连通状态")
    timestamp: datetime = Field(description="服务器当前 UTC 时间")
    uptime_seconds: float = Field(ge=0, description="当前进程已运行秒数")


class PackageCapability(BaseModel):
    """单个依赖的安装状态。"""

    key: str
    label: str
    available: bool
    version: str | None = Field(default=None, description="已安装版本，未知时为 unknown")
    required: bool = Field(description="是否为核心必需依赖")


class CapabilityGroup(BaseModel):
    """按技术栈分组的能力状态。"""

    key: str
    label: str
    description: str
    packages: list[PackageCapability]
    ready: int = Field(ge=0, description="组内已就绪数量")
    total: int = Field(ge=0, description="组内依赖总数")


class SystemInfoResponse(BaseModel):
    """系统信息与能力矩阵。"""

    app_name: str
    version: str
    description: str
    environment: str
    debug: bool
    phase: str
    python_version: str
    platform: str
    database_backend: str
    database_url: str = Field(description="脱敏后的数据库连接地址")
    api_prefix: str
    docs_url: str
    openapi_url: str
    started_at: datetime
    uptime_seconds: float = Field(ge=0)
    capabilities: list[CapabilityGroup]


class DashboardSummary(BaseModel):
    """首页仪表盘聚合数据。"""

    stock_count: int = Field(ge=0, description="股票池公司数量")
    daily_bar_count: int = Field(ge=0, description="已入库日行情数量")
    latest_trade_date: date | None = Field(default=None, description="最新交易日")
    data_status: Literal["empty", "demo", "ready"] = Field(
        description="empty=无股票；demo=只有静态资料；ready=已有行情"
    )
    ai_model_count: int = Field(ge=0, description="已登记的 AI 模型数量（阶段一固定为 0）")
    capability_ready: int = Field(ge=0, description="已就绪依赖数量")
    capability_total: int = Field(ge=0, description="依赖总数")
    phase: str
    timestamp: datetime
