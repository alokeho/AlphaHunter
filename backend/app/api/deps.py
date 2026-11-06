"""API 依赖集合。

集中导出 FastAPI 依赖，后续可在此增加：
- 当前用户
- 数据源实例
- 分页参数
"""

from app.db.session import get_db

__all__ = ["get_db"]
