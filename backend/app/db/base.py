"""SQLAlchemy 声明式基类。

所有 ORM 模型继承 Base。模型的注册由 app.models.__init__ 统一完成，
init_db 在 create_all 前导入模型包，确保 metadata 完整。
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """全局 ORM 基类。

    SQLAlchemy 2.0 的 DeclarativeBase 类型支持完整类型推断，
    后续可在此基础上增加命名约定（constraint naming convention）以配合 Alembic。
    """
