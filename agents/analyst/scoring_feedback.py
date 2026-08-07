"""
scoring_feedback.py – Feedback du modèle de scoring (C4)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.db import get_db_connection
from common.logging import log_action


def get_scoring_accuracy(client_id: str, days: int = 30):
    """Compare les prédictions SQL avec les closed_won réels."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT qualification_score, lead_stage
        FROM leads
        WHERE client_id = %s
          AND qualification_score IS NOT NULL
          AND created_at > NOW() - (%s * INTERVAL '1 DAY')
    """, (client_id, days))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return {"status": "no_data", "samples": 0}

    true_pos = 0
    false_pos = 0
    false_neg = 0

    for score, stage in rows:
        predicted_sql = score >= 61
        actual_closed = stage == 'closed_won'
        if predicted_sql and actual_closed:
            true_pos += 1
        elif predicted_sql and not actual_closed:
            false_pos += 1
        elif not predicted_sql and actual_closed:
            false_neg += 1

    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
    recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "status": "success",
        "samples": true_pos + false_pos + false_neg,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def run_scoring_feedback(client_id: str = "client_test_123"):
    result = get_scoring_accuracy(client_id)
    log_action(
        agent_name="analyst",
        action_type="scoring_feedback",
        input_summary=f"Évaluation du scoring pour {client_id}",
        output_summary=f"F1: {result.get('f1', 0):.2f} ({result.get('samples', 0)} échantillons)",
        client_id=client_id
    )
    return result


if __name__ == "__main__":
    result = run_scoring_feedback()
    if result["status"] == "success":
        print(f"📊 Précision du scoring :")
        print(f"   F1: {result['f1']:.2f}")
        print(f"   Precision: {result['precision']:.2f}")
        print(f"   Recall: {result['recall']:.2f}")
        print(f"   Échantillons: {result['samples']}")
    else:
        print("⚠️ Pas assez de données.")