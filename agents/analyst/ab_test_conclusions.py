"""
ab_test_conclusions.py – Conclusions des A/B tests (C5)
"""

import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.db import get_db_connection
from common.metrics import z_test_p_value
from common.logging import log_action

MIN_CONVERSIONS_PER_VARIANT = 30
CONFIDENCE_LEVEL = 0.95


def get_ab_test_data(client_id: str, test_id: str):
    """Récupère les données d'un test A/B."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT asset_id, conversions, impressions
        FROM content_assets
        WHERE client_id = %s AND variant_group_id = %s
    """, (client_id, test_id))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def conclude_ab_test(client_id: str, test_id: str) -> dict:
    """Déclare un gagnant si le test est significatif."""
    data = get_ab_test_data(client_id, test_id)
    if len(data) < 2:
        return {"status": "insufficient_data", "message": "Moins de 2 variantes"}

    # Vérifier le volume minimum
    for _, conversions, _ in data:
        if conversions < MIN_CONVERSIONS_PER_VARIANT:
            return {"status": "insufficient_data", "message": f"Volume insuffisant ({conversions} conversions)"}

    # Calculer le taux de conversion pour chaque variante
    variants = []
    for asset_id, conversions, impressions in data:
        rate = conversions / impressions if impressions > 0 else 0
        variants.append({"id": asset_id, "rate": rate, "conversions": conversions, "impressions": impressions})

    # Trier par taux décroissant
    variants_sorted = sorted(variants, key=lambda x: x["rate"], reverse=True)
    best = variants_sorted[0]
    second = variants_sorted[1]

    p_value = z_test_p_value(best["conversions"], best["impressions"], second["conversions"], second["impressions"])

    if p_value < (1 - CONFIDENCE_LEVEL):
        return {
            "status": "winner_declared",
            "winner": best["id"],
            "winner_rate": best["rate"],
            "p_value": p_value
        }
    else:
        return {
            "status": "no_winner",
            "best": best["id"],
            "best_rate": best["rate"],
            "p_value": p_value
        }


def run_ab_test_conclusion(client_id: str = "client_test_123", test_id: str = "test_1"):
    result = conclude_ab_test(client_id, test_id)
    log_action(
        agent_name="analyst",
        action_type="ab_test_conclusion",
        input_summary=f"Test {test_id} pour {client_id}",
        output_summary=f"Status: {result['status']}",
        client_id=client_id
    )
    return result


if __name__ == "__main__":
    result = run_ab_test_conclusion()
    print(f"📊 Conclusion A/B Test : {result['status']}")
    if result['status'] == 'winner_declared':
        print(f"   Gagnant : {result['winner']} (taux: {result['winner_rate']:.2%})")
        print(f"   p-value: {result['p_value']:.4f}")