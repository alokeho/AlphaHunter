"""API 总路由。

将所有 v1 子路由挂载到同一个 APIRouter，由 main.py 统一加 /api/v1 前缀。
"""

from fastapi import APIRouter

from app.api.v1.endpoints import dashboard, health, stocks, system

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(system.router)
api_router.include_router(stocks.router)
api_router.include_router(dashboard.router)
