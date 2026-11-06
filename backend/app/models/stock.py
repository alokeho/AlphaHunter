"""股票与日行情 ORM 模型。

第一阶段只建立最核心的两张表：
- stocks：股票静态资料（代码、名称、交易所、板块、行业等）
- daily_bars：日频 OHLCV 行情，为第二阶段的数据同步与因子计算预留

设计说明：
- 股票代码使用不带交易所后缀的 6 位字符串（如 600519），
  交易所单独存字段，便于查询与后续多市场扩展。
- daily_bars 通过 symbol 外键关联 stocks，并设置级联删除。
- (symbol, trade_date) 唯一约束避免重复同步同一交易日数据。
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Stock(TimestampMixin, Base):
    """A 股股票基础资料。"""

    __tablename__ = "stocks"
    __table_args__ = (
        Index("ix_stocks_exchange_active", "exchange", "is_active"),
        Index("ix_stocks_industry", "industry"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(
        String(10), nullable=False, unique=True, index=True, comment="6 位证券代码"
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True, comment="证券简称")
    exchange: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="交易所：SSE/SZSE/BSE"
    )
    market: Mapped[str] = mapped_column(
        String(20), nullable=False, default="主板", comment="板块：主板/创业板/科创板/北交所"
    )
    industry: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="所属行业")
    list_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="上市日期")
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", comment="是否正常上市"
    )
    data_source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="demo",
        server_default="demo",
        comment="资料来源：demo/akshare/manual",
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注说明")

    # 一只股票对应多条日行情。passive_deletes 表示数据库外键负责级联删除。
    daily_bars: Mapped[list[DailyBar]] = relationship(
        back_populates="stock",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        """调试输出，方便在日志中快速识别股票。"""
        return f"<Stock {self.symbol} {self.name}>"


class DailyBar(TimestampMixin, Base):
    """股票日频行情。

    字段采用浮点数，便于 Pandas/NumPy 直接计算；若后续需要严格金额精度，
    可将 price/amount 改为 Numeric，并在服务层统一 Decimal。
    """

    __tablename__ = "daily_bars"
    __table_args__ = (
        UniqueConstraint("symbol", "trade_date", name="uq_daily_bars_symbol_trade_date"),
        Index("ix_daily_bars_trade_date", "trade_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("stocks.symbol", ondelete="CASCADE"),
        nullable=False,
        comment="证券代码",
    )
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, comment="交易日")
    open: Mapped[float] = mapped_column(Float, nullable=False, comment="开盘价（前复权）")
    high: Mapped[float] = mapped_column(Float, nullable=False, comment="最高价（前复权）")
    low: Mapped[float] = mapped_column(Float, nullable=False, comment="最低价（前复权）")
    close: Mapped[float] = mapped_column(Float, nullable=False, comment="收盘价（前复权）")
    volume: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="成交量")
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="成交额")
    pct_change: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="涨跌幅（%）"
    )
    turnover_rate: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="换手率（%）"
    )

    stock: Mapped[Stock] = relationship(back_populates="daily_bars")

    def __repr__(self) -> str:
        """调试输出，包含股票代码与交易日。"""
        return f"<DailyBar {self.symbol} {self.trade_date} close={self.close}>"
