import pytest
from agents.analyst.data_pull import get_all_kpi_data, get_time_to_first_contact, get_response_rate, get_meeting_show_rate


def test_get_all_kpi_data_returns_dict():
    """Teste que get_all_kpi_data retourne un dictionnaire."""
    result = get_all_kpi_data("client_test_123", "2026-07-01", "2026-08-08")
    assert isinstance(result, dict)
    assert "ad_spend" in result
    assert "submissions" in result
    assert "leads_ge_31" in result


def test_get_time_to_first_contact_returns_dict():
    """Teste que get_time_to_first_contact retourne un dictionnaire."""
    result = get_time_to_first_contact("client_test_123", "2026-07-01", "2026-08-08")
    assert isinstance(result, dict)
    assert "total_minutes" in result
    assert "count" in result


def test_get_response_rate_returns_dict():
    """Teste que get_response_rate retourne un dictionnaire."""
    result = get_response_rate("client_test_123", "2026-07-01", "2026-08-08")
    assert isinstance(result, dict)
    assert "replied_first_contacts" in result
    assert "total_first_contacts" in result


def test_get_meeting_show_rate_returns_dict():
    """Teste que get_meeting_show_rate retourne un dictionnaire."""
    result = get_meeting_show_rate("client_test_123", "2026-07-01", "2026-08-08")
    assert isinstance(result, dict)
    assert "total_meetings" in result
    assert "showed_up" in result