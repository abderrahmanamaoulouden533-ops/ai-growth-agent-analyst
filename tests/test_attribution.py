import pytest
from agents.analyst.attribution import get_attribution_breakdown, get_top_performers


def test_get_attribution_breakdown_returns_dict():
    """Teste que get_attribution_breakdown retourne un dictionnaire."""
    result = get_attribution_breakdown("client_test_123", "2026-07-01", "2026-08-08")
    assert isinstance(result, dict)
    assert "campaigns" in result
    assert "ad_sets" in result
    assert "assets" in result


def test_get_top_performers_returns_dict():
    """Teste que get_top_performers retourne un dictionnaire."""
    data = get_attribution_breakdown("client_test_123", "2026-07-01", "2026-08-08")
    result = get_top_performers(data)
    assert isinstance(result, dict)
    assert "best" in result or result["best"] is None