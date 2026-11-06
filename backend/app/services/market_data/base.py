"""行情数据源抽象与领域对象。

为什么要做数据源抽象：
- AKShare 的接口名称、字段和限流策略可能变化；
- 回测与因子计算不应直接依赖某个第三方库；
- 单元测试可以注入 FakeProvider，无需访问网络。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class StockRecord:
    """标准化后的股票静态资料。"""

    symbol: str
    name: str
    exchange: str
    market: str
    industry: str | None = None
    list_date: date | None = None
    data_source: str = "akshare"


@dataclass(frozen=True, slots=True)
class DailyBarRecord:
    """标准化后的日行情记录。"""

    symbol: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    pct_change: float | None = None
    turnover_rate: float | None = None


def normalize_symbol(symbol: str) -> str:
    """把带市场后缀/前缀的代码规范为 6 位纯数字。

    支持示例：
    - "600519"
    - "600519.SH"
    - "SH600519"
    """
    value = symbol.strip().upper()
    for suffix in (".SH", ".SZ", ".BJ"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break

    for prefix in ("SH", "SZ", "BJ"):
        if value.startswith(prefix) and len(value) == 8:
            value = value[2:]
            break

    if len(value) != 6 or not value.isdigit():
        raise ValueError(f"无效的 A 股证券代码：{symbol}")
    return value


def classify_a_share(symbol: str) -> tuple[str, str]:
    """根据 6 位代码推断交易所与板块。

    返回：
    - exchange: SSE（上交所）/ SZSE（深交所）/ BSE（北交所）
    - market: 主板 / 创业板 / 科创板 / 北交所

    说明：该规则覆盖常见 A 股代码段；遇到未来新增代码段时集中在此维护。
    """
    code = normalize_symbol(symbol)

    if code.startswith(("688", "689")):
        return "SSE", "科创板"
    if code.startswith("6"):
        return "SSE", "主板"
    if code.startswith(("300", "301")):
        return "SZSE", "创业板"
    if code.startswith(("000", "001", "002", "003")):
        return "SZSE", "主板"
    if code.startswith(("4", "8", "9")):
        return "BSE", "北交所"

    raise ValueError(f"无法识别证券代码所属板块：{symbol}")


class MarketDataProvider(ABC):
    """行情数据源统一接口。"""

    name: str

    @abstractmethod
    def fetch_stock_list(self) -> list[StockRecord]:
        """获取全市场股票静态资料。"""

    @abstractmethod
    def fetch_daily_bars(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        adjust: str = "qfq",
    ) -> list[DailyBarRecord]:
        """获取单只股票指定区间的前复权日行情。"""
