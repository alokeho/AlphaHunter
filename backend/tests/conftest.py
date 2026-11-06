"""Pytest 公共夹具。

关键：
1. 测试环境变量必须在导入 app 之前设置，否则 Settings 会使用开发数据库。
2. 测试数据库放在 backend/.test-runtime 内，兼容 Windows 沙箱对系统临时目录
   的写入限制，也方便在测试失败后定位数据。
"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_DIR = BACKEND_DIR / ".test-runtime"
TEST_DIR.mkdir(parents=True, exist_ok=True)
TEST_DB = TEST_DIR / "alphahunter-test.db"

# 清理上一次测试可能残留的数据库和 WAL 文件。
for suffix in ("", "-wal", "-shm"):
    stale_file = Path(f"{TEST_DB}{suffix}")
    if stale_file.exists():
        stale_file.unlink()

os.environ["ALPHAHUNTER_ENVIRONMENT"] = "testing"
os.environ["ALPHAHUNTER_DEBUG"] = "false"
os.environ["ALPHAHUNTER_DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["ALPHAHUNTER_SEED_DEMO_DATA"] = "true"
os.environ["ALPHAHUNTER_LOG_LEVEL"] = "WARNING"

# 以下导入必须位于环境变量设置之后。
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """启动完整应用生命周期（含数据库初始化）的测试客户端。"""
    with TestClient(app) as test_client:
        yield test_client
