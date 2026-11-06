"""股票池 API 测试。"""

from fastapi.testclient import TestClient


def test_list_stocks_with_pagination(client: TestClient) -> None:
    """默认演示数据包含 8 只股票，分页字段应正确计算。"""
    response = client.get("/api/v1/stocks", params={"page": 1, "page_size": 3})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 8
    assert payload["pages"] == 3
    assert len(payload["items"]) == 3
    assert payload["items"][0]["symbol"] == "000001"


def test_search_stocks_by_keyword(client: TestClient) -> None:
    """关键词应能匹配股票名称。"""
    response = client.get("/api/v1/stocks", params={"keyword": "茅台"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["symbol"] == "600519"
    assert payload["items"][0]["data_source"] == "demo"


def test_filter_stocks_by_exchange(client: TestClient) -> None:
    """交易所筛选应只返回对应市场的股票。"""
    response = client.get("/api/v1/stocks", params={"exchange": "sse", "page_size": 100})
    assert response.status_code == 200

    items = response.json()["items"]
    assert items
    assert all(item["exchange"] == "SSE" for item in items)


def test_stock_filter_options(client: TestClient) -> None:
    """筛选项应从数据库聚合，且包含交易所中文名。"""
    response = client.get("/api/v1/stocks/filters")
    assert response.status_code == 200

    payload = response.json()
    exchange_values = {item["value"] for item in payload["exchanges"]}
    assert {"SSE", "SZSE"}.issubset(exchange_values)
    assert "食品饮料" in payload["industries"]


def test_get_stock_detail(client: TestClient) -> None:
    """单票详情应返回完整静态资料。"""
    response = client.get("/api/v1/stocks/600519")
    assert response.status_code == 200

    payload = response.json()
    assert payload["name"] == "贵州茅台"
    assert payload["market"] == "主板"
    assert payload["industry"] == "食品饮料"


def test_stock_not_found_uses_standard_error_envelope(client: TestClient) -> None:
    """不存在的股票应返回统一错误结构。"""
    response = client.get("/api/v1/stocks/999999")
    assert response.status_code == 404

    payload = response.json()
    assert payload["code"] == "STOCK_NOT_FOUND"
    assert "999999" in payload["message"]


def test_invalid_symbol_returns_validation_error(client: TestClient) -> None:
    """非 6 位数字代码应被 FastAPI 参数校验拦截。"""
    response = client.get("/api/v1/stocks/abc")
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
