"""仪表盘聚合服务。

阶段一只聚合真实存在的表（股票、日行情）与依赖能力检测结果；
不会伪造收益、回测或模型指标。
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.capabilities import capability_summary
from app.core.config import settings
from app.models.stock import DailyBar, Stock


def get_dashboard_summary(db: Session) -> dict[str, Any]:
    """聚合首页所需统计信息。"""
    stock_count = int(db.scalar(select(func.count()).select_from(Stock)) or 0)
    daily_bar_count = int(db.scalar(select(func.count()).select_from(DailyBar)) or 0)
    latest_trade_date = db.scalar(select(func.max(DailyBar.trade_date)))
    capabilities = capability_summary()

    # 数据状态：
    # - empty：股票池为空，尚未初始化；
    # - demo：只有静态资料，尚无行情，前端应提示用户接入 AKShare；
    # - ready：至少存在一条日行情，可进入数据分析阶段。
    if stock_count == 0:
        data_status = "empty"
    elif daily_bar_count == 0:
        data_status = "demo"
    else:
        data_status = "ready"

    return {
        "stock_count": stock_count,
        "daily_bar_count": daily_bar_count,
        "latest_trade_date": latest_trade_date,
        "data_status": data_status,
        # 阶段一尚未引入模型注册表，该值是真实计数而非模拟指标。
        "ai_model_count": 0,
        "capability_ready": capabilities["ready"],
        "capability_total": capabilities["total"],
        "phase": settings.phase,
        "timestamp": datetime.now(UTC),
    }
