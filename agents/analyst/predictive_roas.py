"""
predictive_roas.py – Prédiction ROAS sur 30 jours (C2)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from common.db import get_db_connection
from common.metrics import stage_conversion_rate
from common.logging import log_action


def get_pipeline_volume(client_id: str) -> dict:
    """
    Volume de leads par stage.

    Args:
        client_id: Identifiant du client.

    Returns:
        dict: {stage: count, ...}
    """
    conn = get_db_connection()
    cur = conn.cursor()
    stages = ['new', 'mql', 'sql', 'contacted', 'meeting_booked']
    result = {}
    for stage in stages:
        cur.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE client_id = %s AND lead_stage = %s
        """, (client_id, stage))
        result[stage] = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def get_historical_conversion_rates(client_id: str) -> dict:
    """
    Taux de conversion historiques par transition.

    Args:
        client_id: Identifiant du client.

    Returns:
        dict: {transition: rate, ...}
    """
    # À remplacer par une vraie requête sur lead_events quand disponible
    return {
        "new_to_mql": 0.35,
        "mql_to_sql": 0.45,
        "sql_to_contacted": 0.60,
        "contacted_to_meeting": 0.50,
        "meeting_to_closed": 0.30
    }


def predict_revenue(client_id: str, avg_deal_value: float = 5000) -> dict:
    """
    Prédit les revenus sur 30 jours.

    Args:
        client_id: Identifiant du client.
        avg_deal_value: Valeur moyenne d'un deal (par défaut 5000€).

    Returns:
        dict: {
            "status": "success" | "insufficient_data",
            "expected_revenue_range": {"low": float, "high": float},
            "assumptions": {
                "avg_deal_value": float,
                "historical_rates": dict,
                "pipeline_volume": dict,
                "total_pipeline": int,
                "projected_deals": float
            }
        }
    """
    pipeline = get_pipeline_volume(client_id)
    rates = get_historical_conversion_rates(client_id)

    total_pipeline = sum(pipeline.values())
    if total_pipeline < 10:
        return {
            "status": "insufficient_data",
            "message": f"Pipeline trop faible ({total_pipeline} leads) pour une prédiction fiable"
        }

    mql_to_sql = pipeline.get('mql', 0) * rates.get('mql_to_sql', 0.45)
    sql_to_meeting = (
        pipeline.get('sql', 0) * 
        rates.get('sql_to_contacted', 0.60) * 
        rates.get('contacted_to_meeting', 0.50)
    )
    meeting_to_closed = pipeline.get('meeting_booked', 0) * rates.get('meeting_to_closed', 0.30)

    total_projected = mql_to_sql + sql_to_meeting + meeting_to_closed

    return {
        "status": "success",
        "expected_revenue_range": {
            "low": total_projected * avg_deal_value * 0.8,
            "high": total_projected * avg_deal_value * 1.2
        },
        "assumptions": {
            "avg_deal_value": avg_deal_value,
            "historical_rates": rates,
            "pipeline_volume": pipeline,
            "total_pipeline": total_pipeline,
            "projected_deals": total_projected
        }
    }


def run_prediction(client_id: str = "client_test_123", avg_deal_value: float = 5000) -> dict:
    """
    Exécute la prédiction et la logue.

    Args:
        client_id: Identifiant du client.
        avg_deal_value: Valeur moyenne d'un deal.

    Returns:
        dict: Résultat de la prédiction.
    """
    result = predict_revenue(client_id, avg_deal_value)
    
    log_action(
        agent_name="analyst",
        action_type="predictive_roas",
        input_summary=f"Prédiction pour {client_id}",
        output_summary=(
            f"Status: {result['status']}, "
            f"Range: {result.get('expected_revenue_range', {}).get('low', 0):.0f} - "
            f"{result.get('expected_revenue_range', {}).get('high', 0):.0f}€"
            if result['status'] == 'success'
            else result.get('message', '')
        ),
        client_id=client_id,
        model_used="rule-based"
    )
    return result


if __name__ == "__main__":
    result = run_prediction()
    if result['status'] == 'success':
        print(f"📈 Prédiction ROAS 30 jours :")
        print(f"   Low: {result['expected_revenue_range']['low']:.0f}€")
        print(f"   High: {result['expected_revenue_range']['high']:.0f}€")
        print(f"   Projeté: {result['assumptions']['projected_deals']:.1f} deals")
    else:
        print(f"⚠️ {result['message']}")