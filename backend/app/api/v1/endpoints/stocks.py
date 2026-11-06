"""股票池端点。

第一阶段提供只读的股票列表、筛选项和单票详情查询。
"""

from __future__ import annotations

from math import ceil

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import NotFoundError
from app.schemas.common import PageResponse
from app.schemas.stock import StockFilterOptions, StockRead
from app.services import stock_service

router = APIRouter(prefix="/stocks", tags=["股票池"])


@router.get(
    "",
    response_model=PageResponse[StockRead],
    summary="分页查询股票池",
)
def list_stocks(
    page: int = Query(default=1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(
        default=None,
        max_length=50,
        description="按代码、名称或行业模糊搜索",
    ),
    exchange: str | None = Query(
        default=None,
        max_length=10,
        description="交易所筛选：SSE/SZSE/BSE",
    ),
    db: Session = Depends(get_db),
) -> PageResponse[StockRead]:
    """返回分页股票列表。"""
    items, total = stock_service.list_stocks(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        exchange=exchange,
    )
    pages = ceil(total / page_size) if total else 0

    return PageResponse[StockRead](
        items=[StockRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/filters",
    response_model=StockFilterOptions,
    summary="获取股票池筛选项",
)
def get_stock_filters(db: Session = Depends(get_db)) -> StockFilterOptions:
    """从真实数据聚合交易所和行业筛选项。

    注意：该静态路径必须定义在 /{symbol} 之前，否则 FastAPI 会把 filters
    当作股票代码匹配，导致 404/422。
    """
    return stock_service.get_filter_options(db)


@router.get(
    "/{symbol}",
    response_model=StockRead,
    summary="查询单只股票详情",
    responses={404: {"description": "股票不存在"}},
)
def get_stock_detail(
    symbol: str = Path(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6 位 A 股证券代码，如 600519",
    ),
    db: Session = Depends(get_db),
) -> StockRead:
    """按证券代码返回股票详情。"""
    stock = stock_service.get_stock_by_symbol(db, symbol)
    if stock is None:
        raise NotFoundError(
            code="STOCK_NOT_FOUND",
            message=f"未找到代码为 {symbol} 的股票",
            details={"symbol": symbol},
        )
    return StockRead.model_validate(stock)
