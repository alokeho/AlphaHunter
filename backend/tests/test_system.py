"""系统信息与仪表盘测试。"""

from fastapi.testclient import TestClient


def test_system_info_exposes_capabilities(client: TestClient) -> None:
    """系统信息应包含应用元数据和按组聚合的依赖矩阵。"""
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200

    payload = response.json()
    assert payload["app_name"] == "AlphaHunter"
    assert payload["environment"] == "testing"
    assert payload["database_backend"] == "sqlite"
    assert payload["phase"].startswith("Phase 1")
    assert len(payload["capabilities"]) == 4

    group_keys = {group["key"] for group in payload["capabilities"]}
    assert group_keys == {"core", "data", "ai", "quant"}


def test_dashboard_summary_uses_real_counts(client: TestClient) -> None:
    """仪表盘应符合演示数据状态：8 只股票、0 条行情、状态 demo。"""
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200

    payload = response.json()
    assert payload["stock_count"] == 8
    assert payload["daily_bar_count"] == 0
    assert payload["data_status"] == "demo"
    assert payload["ai_model_count"] == 0
    assert payload["capability_total"] > 0
