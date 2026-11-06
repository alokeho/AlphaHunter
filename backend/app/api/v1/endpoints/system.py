"""系统信息端点。

面向“系统状态”页面，返回应用元信息、运行环境以及量化/AI 依赖就绪情况。
"""

from __future__ import annotations

import platform
from datetime import UTC, datetime

from fastapi import APIRouter, Request

from app.core.capabilities import inspect_capabilities
from app.core.config import settings
from app.schemas.system import CapabilityGroup, SystemInfoResponse

router = APIRouter(prefix="/system", tags=["系统监控"])


@router.get(
    "/info",
    response_model=SystemInfoResponse,
    summary="获取系统与依赖能力信息",
)
def system_info(request: Request) -> SystemInfoResponse:
    """返回应用运行环境与依赖矩阵。"""
    now = datetime.now(UTC)
    started_at: datetime = getattr(request.app.state, "started_at", now)
    uptime = max((now - started_at).total_seconds(), 0.0)

    capabilities = [CapabilityGroup.model_validate(item) for item in inspect_capabilities()]

    return SystemInfoResponse(
        app_name=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        environment=settings.environment,
        debug=settings.debug,
        phase=settings.phase,
        python_version=platform.python_version(),
        platform=platform.platform(),
        database_backend=settings.database_backend,
        database_url=settings.safe_database_url,
        api_prefix=settings.api_v1_prefix,
        docs_url=request.app.docs_url or "/docs",
        openapi_url=request.app.openapi_url or "/openapi.json",
        started_at=started_at,
        uptime_seconds=round(uptime, 3),
        capabilities=capabilities,
    )
