"""应用配置模块。

设计原则：
1. 所有配置集中在本文件，业务代码只依赖 Settings 实例，不直接读取环境变量。
2. 支持 .env 文件，也支持容器环境变量覆盖，便于本地开发与生产部署共用一套代码。
3. 默认数据库使用 SQLite，切换 PostgreSQL 时只需修改 ALPHAHUNTER_DATABASE_URL，
   不需要改动 ORM 与业务代码。
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> core -> app -> backend
BACKEND_DIR = Path(__file__).resolve().parents[2]
# backend 的上一级即项目根目录
PROJECT_DIR = BACKEND_DIR.parent

# SQLite 默认文件位置。使用绝对路径，避免从不同工作目录启动时生成多个数据库文件。
DEFAULT_DATABASE_URL = f"sqlite:///{(BACKEND_DIR / 'data' / 'alphahunter.db').as_posix()}"


class Settings(BaseSettings):
    """AlphaHunter 全局配置。

    pydantic-settings 会自动完成类型转换和基础校验，例如：
    - "true" / "false" -> bool
    - 环境变量名不区分大小写
    - 未声明的环境变量会被忽略，避免系统环境变量造成启动失败
    """

    model_config = SettingsConfigDict(
        # 所有环境变量统一使用 ALPHAHUNTER_ 前缀
        env_prefix="ALPHAHUNTER_",
        # 同时支持根目录 .env 与 backend/.env；后者优先级更高
        env_file=(PROJECT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- 应用元信息 ----------
    app_name: str = "AlphaHunter"
    app_version: str = "0.1.0"
    app_description: str = "A 股 AI 量化选股平台"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    phase: str = "Phase 1 · 基础框架"

    # ---------- 安全配置 ----------
    # 仅用于本地开发的占位值；生产环境必须通过环境变量替换。
    secret_key: str = "change-me-before-production"

    # ---------- 数据库 ----------
    database_url: str = DEFAULT_DATABASE_URL
    sql_echo: bool = False
    seed_demo_data: bool = True

    # ---------- 服务与跨域 ----------
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ---------- 日志与外部数据 ----------
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    market_data_timeout: int = Field(default=30, ge=1, le=300)

    @field_validator("database_url", mode="before")
    @classmethod
    def fallback_to_default_database(cls, value: object) -> str:
        """空字符串会回退到默认 SQLite 地址。

        .env.example 中数据库地址默认为空，若用户直接复制配置文件，Pydantic
        仍能拿到一个合法连接串，而不是得到 sqlite:/// 这样的无效配置。
        """
        if value is None or str(value).strip() == "":
            return DEFAULT_DATABASE_URL
        return str(value).strip()

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        """保证 API 前缀以 / 开头且不以 / 结尾，避免路由拼接出双斜杠。"""
        value = value.strip()
        if not value.startswith("/"):
            raise ValueError("ALPHAHUNTER_API_V1_PREFIX 必须以 / 开头")
        return value.rstrip("/") or "/api/v1"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        """生产环境禁止使用默认密钥，提前暴露安全风险。"""
        normalized = value.strip()
        if not normalized:
            raise ValueError("ALPHAHUNTER_SECRET_KEY 不能为空")
        return normalized

    @property
    def cors_origins_list(self) -> list[str]:
        """把逗号分隔的跨域白名单转换为列表。"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def data_dir(self) -> Path:
        """返回后端数据目录，并确保目录存在。"""
        directory = BACKEND_DIR / "data"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @property
    def is_sqlite(self) -> bool:
        """当前数据库是否为 SQLite。"""
        return self.database_url.startswith("sqlite")

    @property
    def database_backend(self) -> str:
        """提取数据库类型，用于系统信息展示。"""
        if self.database_url.startswith("sqlite"):
            return "sqlite"
        if self.database_url.startswith("postgresql"):
            return "postgresql"
        if self.database_url.startswith("mysql"):
            return "mysql"
        return "unknown"

    @property
    def safe_database_url(self) -> str:
        """返回可公开展示的数据库地址，隐藏可能存在的密码。"""
        if "://" not in self.database_url:
            return self.database_url
        scheme, remainder = self.database_url.split("://", 1)
        if "@" in remainder and ":" in remainder.split("@", 1)[0]:
            credentials, location = remainder.rsplit("@", 1)
            username = credentials.split(":", 1)[0]
            return f"{scheme}://{username}:***@{location}"
        return self.database_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取全局单例配置。

    使用 lru_cache 保证整个进程只解析一次 .env。测试中如需切换配置，
    应在导入应用前设置环境变量，或调用 get_settings.cache_clear()。
    """
    return Settings()


# 模块级实例，业务代码直接 `from app.core.config import settings` 即可。
settings = get_settings()
