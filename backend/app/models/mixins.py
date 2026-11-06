"""ORM 通用字段 Mixin。

把创建时间、更新时间等审计字段集中管理，避免每张表重复声明。
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """为模型提供 created_at 与 updated_at 字段。"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        # Python 侧默认值使用带时区的 UTC 时间，保证跨环境一致。
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
        comment="最后更新时间",
    )
