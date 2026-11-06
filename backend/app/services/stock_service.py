"""股票资料查询服务。

本模块封装所有股票相关的数据库查询，路由层不直接拼接 SQLAlchemy 语句。
"""

from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.stock import Stock
from app.schemas.stock import SelectOption, StockFilterOptions

# 交易所代码与中文名称的映射，供前端筛选器展示。
EXCHANGE_LABELS: dict[str, str] = {
    "SSE": "上海证券交易所",
    "SZSE": "深圳证券交易所",
    "BSE": "北京证券交易所",
}


def _build_stock_query(
    keyword: str | None = None,
    exchange: str | None = None,
) -> tuple[Select[tuple[Stock]], list[object]]:
    """构造带筛选条件的查询并返回条件列表。

    把“查询语句”和“条件”分开返回，便于列表查询与总数查询复用同一组条件。
    """
    conditions: list[object] = []

    if keyword:
        # 关键词同时匹配代码、名称、行业。使用 ilike 兼容 SQLite 与 PostgreSQL。
        pattern = f"%{keyword.strip()}%"
        conditions.append(
            or_(
                Stock.symbol.ilike(pattern),
                Stock.name.ilike(pattern),
                Stock.industry.ilike(pattern),
            )
        )

    if exchange:
        conditions.append(Stock.exchange == exchange.strip().upper())

    stmt = select(Stock).where(*conditions)
    return stmt, conditions


def list_stocks(
    db: Session,
    *,
    page: int,
    page_size: int,
    keyword: str | None = None,
    exchange: str | None = None,
) -> tuple[list[Stock], int]:
    """分页查询股票列表，返回 (当前页数据, 总数)。

    排序规则：代码升序，保证分页结果稳定可复现。
    """
    stmt, conditions = _build_stock_query(keyword=keyword, exchange=exchange)
    count_stmt = select(func.count()).select_from(Stock).where(*conditions)

    total = int(db.scalar(count_stmt) or 0)
    offset = (page - 1) * page_size
    items = list(
        db.scalars(
            stmt.order_by(Stock.symbol.asc()).offset(offset).limit(page_size)
        ).all()
    )
    return items, total


def get_stock_by_symbol(db: Session, symbol: str) -> Stock | None:
    """按 6 位代码查询单只股票。"""
    return db.scalar(select(Stock).where(Stock.symbol == symbol))


def get_filter_options(db: Session) -> StockFilterOptions:
    """从数据库聚合交易所与行业筛选项。"""
    exchanges = list(
        db.scalars(
            select(Stock.exchange)
            .where(Stock.is_active.is_(True))
            .distinct()
            .order_by(Stock.exchange.asc())
        ).all()
    )
    industries = list(
        db.scalars(
            select(Stock.industry)
            .where(Stock.industry.is_not(None), Stock.industry != "")
            .distinct()
            .order_by(Stock.industry.asc())
        ).all()
    )

    exchange_options = [
        SelectOption(value=item, label=EXCHANGE_LABELS.get(item, item)) for item in exchanges
    ]
    return StockFilterOptions(
        exchanges=exchange_options,
        industries=[item for item in industries if item],
    )
