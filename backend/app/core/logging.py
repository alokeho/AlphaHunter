"""日志配置模块。

统一配置控制台日志格式，避免各模块各自调用 basicConfig 导致重复处理器。
容器环境下日志输出到 stdout，便于 Docker / 云平台采集。
"""

from __future__ import annotations

import logging
import sys

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    """初始化根日志器。

    该函数可重复调用：如果根日志器已有 AlphaHunter 处理器，则只更新级别，
    不会重复添加 handler，从而避免同一条日志被打印多次。
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    alpha_handler_exists = any(
        getattr(handler, "_alphahunter_handler", False) for handler in root_logger.handlers
    )

    if not alpha_handler_exists:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(settings.log_level)
        console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        # 使用私有标记识别本应用添加的 handler，便于幂等初始化。
        console_handler._alphahunter_handler = True  # type: ignore[attr-defined]
        root_logger.addHandler(console_handler)

    # 统一 uvicorn 访问日志与错误日志的级别，避免其覆盖全局设置。
    logging.getLogger("uvicorn").setLevel(settings.log_level)
    logging.getLogger("uvicorn.access").setLevel(settings.log_level)
    logging.getLogger("uvicorn.error").setLevel(settings.log_level)

    # SQLAlchemy 在 sql_echo 关闭时无需重复输出 INFO 日志。
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.sql_echo else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """获取带命名空间的日志器，便于按模块过滤日志。"""
    return logging.getLogger(name)
