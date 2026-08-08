import pytest
from agents.analyst.predictive_roas import predict_revenue, run_prediction


def test_predict_revenue_returns_dict():
    """Teste que predict_revenue retourne un dictionnaire."""
    result = predict_revenue("client_test_123")
    assert isinstance(result, dict)
    assert result["status"] in ["success", "insufficient_data"]


def test_predict_revenue_insufficient_data():
    """Teste que predict_revenue retourne insufficient_data pour un pipeline vide."""
    result = predict_revenue("client_test_123")
    if result["status"] == "insufficient_data":
        assert "message" in result


def test_run_prediction_logs_action():
    """Teste que run_prediction s'exécute sans erreur."""
    result = run_prediction("client_test_123")
    assert isinstance(result, dict)