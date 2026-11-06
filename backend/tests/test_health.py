"""健康检查与根路由测试。"""

from fastapi.testclient import TestClient


def test_root_returns_service_metadata(client: TestClient) -> None:
    """根路径应返回服务名称与文档入口。"""
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "AlphaHunter"
    assert payload["docs"] == "/docs"
    assert payload["health"] == "/api/v1/health"


def test_health_check_is_ok(client: TestClient) -> None:
    """健康检查应验证数据库可用，并返回运行环境。"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] == "ok"
    assert payload["service"] == "AlphaHunter"
    assert payload["environment"] == "testing"
    assert payload["uptime_seconds"] >= 0
    assert "X-Process-Time-Ms" in response.headers
