"""运行环境能力检测模块。

第一阶段不训练模型，也不执行回测，但需要让用户清楚当前安装环境是否具备
后续阶段的依赖。本模块只做“包是否可导入 + 版本号读取”，不会导入大型库，
因此对启动速度几乎没有影响。
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PackageSpec:
    """单个依赖包的检测定义。"""

    key: str
    label: str
    distribution: str
    module: str
    required: bool = False


# 依赖分组：与项目技术栈保持一致，前端系统页直接渲染这些分组。
CAPABILITY_GROUPS: tuple[dict[str, Any], ...] = (
    {
        "key": "core",
        "label": "基础服务",
        "description": "Web 服务、数据校验与 ORM 核心",
        "packages": (
            PackageSpec("fastapi", "FastAPI", "fastapi", "fastapi", required=True),
            PackageSpec("uvicorn", "Uvicorn", "uvicorn", "uvicorn", required=True),
            PackageSpec("pydantic", "Pydantic", "pydantic", "pydantic", required=True),
            PackageSpec(
                "pydantic-settings",
                "Pydantic Settings",
                "pydantic-settings",
                "pydantic_settings",
                required=True,
            ),
            PackageSpec(
                "sqlalchemy", "SQLAlchemy", "SQLAlchemy", "sqlalchemy", required=True
            ),
        ),
    },
    {
        "key": "data",
        "label": "数据与分析",
        "description": "A 股行情获取、清洗与科学计算",
        "packages": (
            PackageSpec("akshare", "AKShare", "akshare", "akshare"),
            PackageSpec("pandas", "Pandas", "pandas", "pandas"),
            PackageSpec("numpy", "NumPy", "numpy", "numpy"),
            PackageSpec("scipy", "SciPy", "scipy", "scipy"),
        ),
    },
    {
        "key": "ai",
        "label": "机器学习",
        "description": "选股模型训练与超参数搜索",
        "packages": (
            PackageSpec(
                "scikit-learn", "scikit-learn", "scikit-learn", "sklearn"
            ),
            PackageSpec("lightgbm", "LightGBM", "lightgbm", "lightgbm"),
            PackageSpec("xgboost", "XGBoost", "xgboost", "xgboost"),
            PackageSpec("optuna", "Optuna", "optuna", "optuna"),
        ),
    },
    {
        "key": "quant",
        "label": "量化研究",
        "description": "技术指标计算与策略回测",
        "packages": (
            PackageSpec("pandas-ta", "pandas-ta", "pandas-ta", "pandas_ta"),
            PackageSpec("backtrader", "Backtrader", "backtrader", "backtrader"),
        ),
    },
)


def _get_package_version(dist: str, module: str) -> str | None:
    """读取已安装包版本。

    注意：优先检查模块是否可以导入，再读取 distribution 元数据。
    某些包可能只留下元数据而模块文件损坏，此时视为不可用。
    """
    try:
        if importlib.util.find_spec(module) is None:
            return None
    except (ImportError, ModuleNotFoundError, ValueError):
        # find_spec 在父模块缺失或路径异常时会抛错，统一视为未安装。
        return None

    try:
        return importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        # 源码直接运行、未安装元数据时仍可用，只是无法显示版本。
        return "unknown"


def inspect_capabilities() -> list[dict[str, Any]]:
    """返回前端可直接消费的能力清单。

    返回结构示例：
    [
      {
        "key": "core",
        "label": "基础服务",
        "description": "...",
        "packages": [
          {"key": "fastapi", "label": "FastAPI", "available": true,
           "version": "0.115.8", "required": true}
        ],
        "ready": 5,
        "total": 5
      }
    ]
    """
    result: list[dict[str, Any]] = []

    for group in CAPABILITY_GROUPS:
        package_items: list[dict[str, Any]] = []
        for spec in group["packages"]:
            version = _get_package_version(spec.distribution, spec.module)
            package_items.append(
                {
                    "key": spec.key,
                    "label": spec.label,
                    "available": version is not None,
                    "version": version,
                    "required": spec.required,
                }
            )

        result.append(
            {
                "key": group["key"],
                "label": group["label"],
                "description": group["description"],
                "packages": package_items,
                "ready": sum(1 for item in package_items if item["available"]),
                "total": len(package_items),
            }
        )

    return result


def capability_summary() -> dict[str, int]:
    """汇总依赖就绪情况，供仪表盘统计卡片使用。"""
    groups = inspect_capabilities()
    return {
        "ready": sum(group["ready"] for group in groups),
        "total": sum(group["total"] for group in groups),
    }
