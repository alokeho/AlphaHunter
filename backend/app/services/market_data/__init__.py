"""行情数据源适配层。

通过抽象接口隔离 AKShare 等外部数据源，业务层只依赖 MarketDataProvider。
阶段一实现 AKShare 适配器但不在启动时联网，后续可在同步任务中直接复用。
"""

from app.services.market_data.akshare_provider import AkshareMarketDataProvider
from app.services.market_data.base import (
    DailyBarRecord,
    MarketDataProvider,
    StockRecord,
    classify_a_share,
    normalize_symbol,
)


def create_market_data_provider(name: str = "akshare") -> MarketDataProvider:
    """根据名称创建行情数据源。

    预留多数据源扩展点：未来可以增加 Tushare、聚宽或本地 Parquet 数据源。
    """
    providers: dict[str, type[MarketDataProvider]] = {
        "akshare": AkshareMarketDataProvider,
    }
    provider_class = providers.get(name.lower())
    if provider_class is None:
        raise ValueError(f"不支持的行情数据源：{name}")
    return provider_class()


__all__ = [
    "DailyBarRecord",
    "MarketDataProvider",
    "StockRecord",
    "AkshareMarketDataProvider",
    "classify_a_share",
    "create_market_data_provider",
    "normalize_symbol",
]
