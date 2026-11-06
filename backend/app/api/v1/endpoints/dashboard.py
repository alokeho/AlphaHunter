"""仪表盘端点。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.system import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="获取首页聚合统计",
)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    """返回股票数量、行情数量、数据状态与依赖就绪度。"""
    return DashboardSummary.model_validate(get_dashboard_summary(db))
