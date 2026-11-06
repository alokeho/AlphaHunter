"""行情数据适配层纯函数测试（不访问网络）。"""

import pytest
from app.services.market_data.base import classify_a_share, normalize_symbol


def test_normalize_symbol_supports_common_formats() -> None:
    """应兼容裸代码、后缀代码和前缀代码。"""
    assert normalize_symbol("600519") == "600519"
    assert normalize_symbol("600519.SH") == "600519"
    assert normalize_symbol("sz000001") == "000001"


@pytest.mark.parametrize(
    ("symbol", "expected"),
    [
        ("600519", ("SSE", "主板")),
        ("688981", ("SSE", "科创板")),
        ("300750", ("SZSE", "创业板")),
        ("000001", ("SZSE", "主板")),
        ("830799", ("BSE", "北交所")),
    ],
)
def test_classify_a_share(symbol: str, expected: tuple[str, str]) -> None:
    """主流代码段应映射到正确交易所与板块。"""
    assert classify_a_share(symbol) == expected


def test_invalid_symbol_raises_value_error() -> None:
    """非法代码应明确抛错，避免写入错误数据。"""
    with pytest.raises(ValueError):
        normalize_symbol("ABC")
