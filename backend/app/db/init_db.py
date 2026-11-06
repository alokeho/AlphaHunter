"""数据库初始化脚本。

使用方式（在 backend 目录下）：
    python -m app.db.init_db
    python -m app.db.init_db --no-seed

启动 FastAPI 时也会自动执行同一初始化逻辑，保证首次启动即可用。
第一阶段使用 SQLAlchemy metadata.create_all；当表结构开始频繁演进时，
应在后续阶段引入 Alembic 迁移，而不是继续依赖 create_all。
"""

from __future__ import annotations

import argparse
import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.base import Base
from app.db.seed import seed_demo_stocks
from app.db.session import SessionLocal, dispose_engine, engine
from app.models import DailyBar, Stock  # noqa: F401  # 导入以注册表结构

logger = get_logger(__name__)


def _database_stats(db: Session) -> dict[str, int]:
    """读取初始化后的核心表计数。"""
    stock_count = db.scalar(select(func.count()).select_from(Stock)) or 0
    bar_count = db.scalar(select(func.count()).select_from(DailyBar)) or 0
    return {"stocks": int(stock_count), "daily_bars": int(bar_count)}


def initialize_database(with_seed: bool | None = None) -> dict[str, int | bool]:
    """创建表结构并按配置写入演示数据。

    参数：
    - with_seed: 是否写入演示股票。None 表示使用配置项 seed_demo_data；
      True/False 用于测试或 CLI 显式覆盖。

    返回：
    - created: 是否执行了建表检查
    - seeded: 本次新增的演示股票数量
    - stocks / daily_bars: 初始化后的记录数
    """
    # data_dir 是 property，读取时会确保目录存在，避免 SQLite 无法创建文件。
    data_dir = settings.data_dir
    logger.debug("后端数据目录：%s", data_dir)
    should_seed = settings.seed_demo_data if with_seed is None else with_seed

    logger.info("正在检查数据库表结构，数据库类型=%s", settings.database_backend)
    Base.metadata.create_all(bind=engine)

    seeded = 0
    with SessionLocal() as db:
        if should_seed:
            seeded = seed_demo_stocks(db)
            if seeded:
                logger.info("已写入 %s 条演示股票数据（data_source=demo）", seeded)
        stats = _database_stats(db)

    logger.info("数据库初始化完成：股票 %s 条，日行情 %s 条", stats["stocks"], stats["daily_bars"])
    return {"created": True, "seeded": seeded, **stats}


def main() -> None:
    """命令行入口。"""
    configure_logging()
    parser = argparse.ArgumentParser(description="初始化 AlphaHunter SQLite 数据库")
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="只创建表结构，不写入演示股票数据",
    )
    args = parser.parse_args()

    try:
        summary = initialize_database(with_seed=not args.no_seed)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    except Exception as exc:  # noqa: BLE001
        # CLI 场景需要把失败原因明确输出给使用者，同时保留日志堆栈。
        logger.exception("数据库初始化失败")
        raise SystemExit(f"数据库初始化失败：{exc}") from exc
    finally:
        dispose_engine()


if __name__ == "__main__":
    main()
