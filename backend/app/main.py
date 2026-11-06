"""FastAPI 应用入口。

启动方式（在 backend 目录下）：
    uvicorn app.main:app --reload
或者：
    python -m app.main

应用启动时会自动：
1. 初始化日志；
2. 检查数据库表结构；
3. 写入演示股票（可通过配置关闭）；
4. 注册路由、CORS 与统一异常处理。
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.init_db import initialize_database
from app.db.session import dispose_engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """管理应用的启动与关闭生命周期。

    在 yield 之前的代码会在 Uvicorn 开始接收请求前执行，
    因此数据库表一定已经创建完成，不会出现首次请求表不存在的竞态。
    """
    configure_logging()
    application.state.started_at = datetime.now(UTC)
    logger.info(
        "%s v%s 启动中 | 环境=%s | 数据库=%s",
        settings.app_name,
        settings.app_version,
        settings.environment,
        settings.database_backend,
    )

    summary = initialize_database()
    application.state.database_summary = summary
    logger.info("API 已就绪，文档地址：http://%s:%s/docs", settings.host, settings.port)

    yield

    logger.info("%s 正在关闭，释放数据库连接池", settings.app_name)
    dispose_engine()


def create_application() -> FastAPI:
    """应用工厂。

    使用工厂函数便于测试中创建独立实例，也便于未来按环境注入不同配置。
    """
    application = FastAPI(
        title=f"{settings.app_name} API",
        version=settings.app_version,
        description=settings.app_description,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters={"persistAuthorization": True},
        openapi_tags=[
            {"name": "系统监控", "description": "健康检查、运行环境与依赖能力"},
            {"name": "股票池", "description": "股票静态资料查询与筛选"},
            {"name": "仪表盘", "description": "平台首页聚合统计"},
        ],
    )

    # 跨域仅放行配置中的前端地址；生产环境不推荐使用 "*"。
    if settings.cors_origins_list:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Process-Time-Ms"],
        )

    @application.middleware("http")
    async def add_process_time_header(request: Request, call_next: Any) -> Any:
        """记录请求处理耗时，便于前端与网关观测性能。"""
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response

    register_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        """根路径提供最小导航信息，方便快速确认服务已启动。"""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "phase": settings.phase,
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
        }

    return application


app = create_application()


if __name__ == "__main__":
    # 支持 python -m app.main 直接启动，读取 .env 中的 HOST/PORT。
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
