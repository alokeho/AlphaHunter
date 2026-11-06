"""数据库引擎与会话管理。

关键设计：
1. 同步 SQLAlchemy + SQLite 是第一阶段最稳妥的组合，减少异步驱动和线程问题。
2. 通过 FastAPI 依赖 get_db 为每个请求创建独立 Session，请求结束自动关闭。
3. SQLite 开启外键约束与 WAL 模式，提升并发读性能与数据完整性。
4. 后续切换 PostgreSQL 只需要修改配置中的 DATABASE_URL。
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# SQLite 在多线程 FastAPI 服务中需要关闭 check_same_thread。
# timeout 用于遇到写锁时等待，而不是立即抛出 database is locked。
_connect_args: dict[str, Any] = {}
if settings.is_sqlite:
    _connect_args = {"check_same_thread": False, "timeout": 30}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
    echo=settings.sql_echo,
    future=True,
)


if settings.is_sqlite:

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: Any, _connection_record: Any) -> None:
        """每次建立 SQLite 连接时设置关键 PRAGMA。

        - foreign_keys=ON：SQLite 默认不启用外键，必须显式开启。
        - journal_mode=WAL：允许读写并发，对 Web 服务更友好。
        - busy_timeout=30000：写冲突时最多等待 30 秒。
        """
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")
        finally:
            cursor.close()


# expire_on_commit=False 避免提交后访问 ORM 属性触发额外查询，
# 对 API 响应序列化更友好。
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 数据库依赖。

    使用方式：
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # 未捕获异常时回滚当前事务，避免脏数据占用连接。
        db.rollback()
        raise
    finally:
        db.close()


def check_database_connection() -> bool:
    """执行轻量查询验证数据库可用性。"""
    from sqlalchemy import text

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def dispose_engine() -> None:
    """释放连接池。

    应用关闭或测试结束时调用；SQLite 文件模式下可确保 WAL 文件正确收尾。
    """
    engine.dispose()
