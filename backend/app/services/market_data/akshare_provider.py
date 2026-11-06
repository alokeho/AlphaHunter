"""AKShare 行情数据源实现。

第一阶段只实现适配器并通过单元测试验证代码规范化逻辑，不在应用启动时联网。
后续实现“数据同步任务”时，可直接调用本类，把返回的标准化记录写入数据库。

安装说明：
    AKShare 已在 requirements.txt 中声明。若本地未安装，调用本类方法会抛出
    DataProviderError，而不会导致整个 FastAPI 进程启动失败。
"""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from app.core.exceptions import DataProviderError
from app.core.logging import get_logger
from app.services.market_data.base import (
    DailyBarRecord,
    MarketDataProvider,
    StockRecord,
    classify_a_share,
    normalize_symbol,
)

logger = get_logger(__name__)

# AKShare 返回的中文列名 -> 内部字段名。
_DAILY_COLUMN_MAP: dict[str, str] = {
    "日期": "trade_date",
    "开盘": "open",
    "收盘": "close",
    "最高": "high",
    "最低": "low",
    "成交量": "volume",
    "成交额": "amount",
    "涨跌幅": "pct_change",
    "换手率": "turnover_rate",
}


class AkshareMarketDataProvider(MarketDataProvider):
    """基于 AKShare 的 A 股数据源。"""

    name = "akshare"

    @staticmethod
    def _import_akshare() -> Any:
        """延迟导入 AKShare。

        延迟导入可以让健康检查、股票查询等接口在未安装 AKShare 时仍可用；
        只有真正执行数据同步时才需要该依赖。
        """
        try:
            import akshare as ak
        except ImportError as exc:
            raise DataProviderError(
                message="未安装 AKShare，无法获取行情数据，请先安装 requirements.txt",
                details={"reason": str(exc)},
            ) from exc
        return ak

    def fetch_stock_list(self) -> list[StockRecord]:
        """获取 A 股股票代码与名称列表。

        AKShare 接口：stock_info_a_code_name()
        该接口只返回 code/name 两列，不含行业；行业资料留待后续用行业接口补充。
        """
        ak = self._import_akshare()
        try:
            frame = ak.stock_info_a_code_name()
        except Exception as exc:  # noqa: BLE001
            # 第三方库异常类型不稳定，这里统一包装为可观测的业务异常。
            logger.exception("AKShare 获取股票列表失败")
            raise DataProviderError(
                message="AKShare 股票列表接口调用失败，请稍后重试",
                details={"reason": str(exc)},
            ) from exc

        if not isinstance(frame, pd.DataFrame) or frame.empty:
            raise DataProviderError(message="AKShare 返回的股票列表为空")

        if "code" not in frame.columns or "name" not in frame.columns:
            raise DataProviderError(
                message="AKShare 股票列表字段发生变化，缺少 code/name 列",
                details={"columns": [str(column) for column in frame.columns]},
            )

        records: list[StockRecord] = []
        seen: set[str] = set()

        for row in frame.to_dict(orient="records"):
            try:
                symbol = normalize_symbol(str(row["code"]))
                exchange, market = classify_a_share(symbol)
            except ValueError:
                # 非标准代码（如指数、退市代码）直接跳过，不让单条脏数据中断全量同步。
                continue

            if symbol in seen:
                continue
            seen.add(symbol)
            records.append(
                StockRecord(
                    symbol=symbol,
                    name=str(row["name"]).strip(),
                    exchange=exchange,
                    market=market,
                    data_source=self.name,
                )
            )

        logger.info("AKShare 股票列表解析完成，共 %s 条", len(records))
        return records

    def fetch_daily_bars(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        adjust: str = "qfq",
    ) -> list[DailyBarRecord]:
        """获取指定股票与日期区间的日行情。

        参数 adjust：
        - qfq：前复权，适合因子计算与回测；
        - hfq：后复权；
        - "": 不复权。
        """
        if start_date > end_date:
            raise ValueError("start_date 不能晚于 end_date")
        if adjust not in {"qfq", "hfq", ""}:
            raise ValueError("adjust 仅支持 qfq / hfq / 空字符串")

        code = normalize_symbol(symbol)
        ak = self._import_akshare()

        try:
            frame = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust=adjust,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("AKShare 获取日行情失败 symbol=%s", code)
            raise DataProviderError(
                message=f"获取 {code} 日行情失败，请检查网络或稍后重试",
                details={"symbol": code, "reason": str(exc)},
            ) from exc

        if not isinstance(frame, pd.DataFrame) or frame.empty:
            return []

        missing_columns = [column for column in _DAILY_COLUMN_MAP if column not in frame.columns]
        if missing_columns:
            raise DataProviderError(
                message="AKShare 日行情字段发生变化",
                details={"missing_columns": missing_columns},
            )

        records: list[DailyBarRecord] = []
        for row in frame.to_dict(orient="records"):
            try:
                trade_date = pd.to_datetime(row["日期"]).date()
                open_price = self._to_float(row["开盘"])
                high_price = self._to_float(row["最高"])
                low_price = self._to_float(row["最低"])
                close_price = self._to_float(row["收盘"])

                # OHLC 缺失的记录无法用于回测，跳过而不是写入脏数据。
                if None in (open_price, high_price, low_price, close_price):
                    continue

                records.append(
                    DailyBarRecord(
                        symbol=code,
                        trade_date=trade_date,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        volume=self._to_float(row["成交量"]) or 0.0,
                        amount=self._to_float(row["成交额"]) or 0.0,
                        pct_change=self._to_float(row["涨跌幅"]),
                        turnover_rate=self._to_float(row["换手率"]),
                    )
                )
            except (TypeError, ValueError, KeyError):
                logger.warning("跳过一条无法解析的日行情记录 symbol=%s", code)
                continue

        return records

    @staticmethod
    def _to_float(value: Any) -> float | None:
        """把 Pandas/NumPy 数值安全转换为 Python float。

        NaN、None、空字符串统一返回 None，避免 JSON 序列化出现 NaN。
        """
        if value is None:
            return None
        try:
            if pd.isna(value):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
