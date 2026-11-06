"""健康检查端点。

用途：
- Docker healthcheck
- 前端顶部在线状态指示
- 负载均衡/监控系统探活

该接口会真实执行 SELECT 1，不做“假健康”返回。
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.exceptions import AppException
from app.schemas.system import HealthResponse

router = APIRouter(tags=["系统监控"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="服务健康检查",
    description="检查 API 进程与数据库连接；数据库异常时返回 HTTP 503。",
)
def health_check(request: Request, db: Session = Depends(get_db)) -> HealthResponse:
    """返回服务与数据库健康状态。"""
    try:
        db.execute(text("SELECT 1"))
        database_status = "ok"
    except SQLAlchemyError as exc:
        # 数据库不可用时返回 503，便于容器编排与监控系统识别。
        raise AppException(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="数据库连接异常，服务暂不可用",
            details={"reason": str(exc)} if settings.debug else None,
        ) from exc

    now = datetime.now(UTC)
    started_at: datetime = getattr(request.app.state, "started_at", now)
    uptime = max((now - started_at).total_seconds(), 0.0)

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        phase=settings.phase,
        database=database_status,
        timestamp=now,
        uptime_seconds=round(uptime, 3),
    )
