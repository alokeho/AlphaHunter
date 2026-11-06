"""演示数据种子。

第一阶段尚未执行真实行情同步，为了让前端和 API 有可展示、可联调的数据，
初始化时写入一组具有代表性的 A 股股票静态资料。

重要说明：
- 这里只写入“股票代码/名称/行业”等公开静态信息，不伪造行情和收益数据；
- 所有种子数据标记 data_source="demo"，前端会提示用户；
- 当用户后续接入 AKShare 真实数据后，可按 symbol 幂等更新资料。
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock import Stock

# 覆盖沪深主板、创业板、科创板与不同行业，便于验证筛选与展示逻辑。
DEMO_STOCKS: tuple[dict[str, Any], ...] = (
    {
        "symbol": "600519",
        "name": "贵州茅台",
        "exchange": "SSE",
        "market": "主板",
        "industry": "食品饮料",
        "list_date": date(2001, 8, 27),
        "description": "上交所主板，白酒行业代表公司。",
    },
    {
        "symbol": "000001",
        "name": "平安银行",
        "exchange": "SZSE",
        "market": "主板",
        "industry": "银行",
        "list_date": date(1991, 4, 3),
        "description": "深交所主板，股份制商业银行。",
    },
    {
        "symbol": "300750",
        "name": "宁德时代",
        "exchange": "SZSE",
        "market": "创业板",
        "industry": "电力设备",
        "list_date": date(2018, 6, 11),
        "description": "深交所创业板，动力电池与储能龙头。",
    },
    {
        "symbol": "688981",
        "name": "中芯国际",
        "exchange": "SSE",
        "market": "科创板",
        "industry": "半导体",
        "list_date": date(2020, 7, 16),
        "description": "上交所科创板，集成电路晶圆代工企业。",
    },
    {
        "symbol": "601318",
        "name": "中国平安",
        "exchange": "SSE",
        "market": "主板",
        "industry": "非银金融",
        "list_date": date(2007, 3, 1),
        "description": "上交所主板，综合金融集团。",
    },
    {
        "symbol": "000858",
        "name": "五粮液",
        "exchange": "SZSE",
        "market": "主板",
        "industry": "食品饮料",
        "list_date": date(1998, 4, 27),
        "description": "深交所主板，浓香型白酒企业。",
    },
    {
        "symbol": "002594",
        "name": "比亚迪",
        "exchange": "SZSE",
        "market": "主板",
        "industry": "汽车",
        "list_date": date(2011, 6, 30),
        "description": "深交所主板，新能源汽车与电池制造商。",
    },
    {
        "symbol": "600036",
        "name": "招商银行",
        "exchange": "SSE",
        "market": "主板",
        "industry": "银行",
        "list_date": date(2002, 4, 9),
        "description": "上交所主板，全国性股份制商业银行。",
    },
)


def seed_demo_stocks(db: Session) -> int:
    """幂等写入演示股票，返回新增数量。

    幂等策略：先查询已有 symbol，只插入缺失项，不覆盖用户后续维护的数据。
    """
    existing_symbols = set(db.scalars(select(Stock.symbol)).all())
    new_stocks = [
        Stock(
            **item,
            is_active=True,
            data_source="demo",
        )
        for item in DEMO_STOCKS
        if item["symbol"] not in existing_symbols
    ]

    if not new_stocks:
        return 0

    db.add_all(new_stocks)
    db.commit()
    return len(new_stocks)
