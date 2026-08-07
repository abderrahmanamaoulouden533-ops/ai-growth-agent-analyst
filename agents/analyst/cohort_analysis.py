"""
cohort_analysis.py – Analyse de cohortes (C3)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from common.db import get_db_connection
from common.logging import log_action


def get_cohort_data(client_id: str, weeks: int = 8):
    """Retourne les données de cohorte par semaine d'acquisition."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        WITH cohorts AS (
            SELECT 
                DATE_TRUNC('week', created_at) as cohort_week,
                source,
                COUNT(*) as total_leads,
                COUNT(CASE WHEN lead_stage = 'closed_won' THEN 1 END) as closed_won
            FROM leads
            WHERE client_id = %s
              AND created_at > NOW() - (%s * INTERVAL '1 WEEK')
              AND source IS NOT NULL
            GROUP BY cohort_week, source
        )
        SELECT * FROM cohorts ORDER BY cohort_week DESC
    """, (client_id, weeks))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_cohort_summary(client_id: str):
    """Calcule les taux de conversion par source."""
    data = get_cohort_data(client_id)
    results = {}
    for cohort_week, source, total, closed in data:
        if source not in results:
            results[source] = {"total": 0, "closed": 0}
        results[source]["total"] += total
        results[source]["closed"] += closed

    for source in results:
        results[source]["conversion_rate"] = (
            results[source]["closed"] / results[source]["total"] * 100
            if results[source]["total"] > 0 else 0
        )
    return results


def run_cohort_analysis(client_id: str = "client_test_123"):
    """Exécute l'analyse et la logue."""
    summary = get_cohort_summary(client_id)
    
    if not summary:
        print("⚠️ Aucune donnée de cohorte disponible.")
        return {"status": "no_data", "message": "Aucune source attribuée"}

    best_source = max(summary, key=lambda x: summary[x]["conversion_rate"])
    
    log_action(
        agent_name="analyst",
        action_type="cohort_analysis",
        input_summary=f"Analyse pour {client_id}",
        output_summary=f"Meilleure source: {best_source} ({summary[best_source]['conversion_rate']:.1f}%)",
        client_id=client_id
    )
    
    return {
        "status": "success",
        "summary": summary,
        "best_source": best_source,
        "best_rate": summary[best_source]["conversion_rate"]
    }


if __name__ == "__main__":
    result = run_cohort_analysis()
    if result["status"] == "success":
        print("📊 Analyse de cohortes :")
        for source, data in result["summary"].items():
            print(f"  {source}: {data['conversion_rate']:.1f}% ({data['closed']}/{data['total']})")
        print(f"\n🏆 Meilleure source : {result['best_source']} ({result['best_rate']:.1f}%)")