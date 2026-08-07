"""
anomaly_detector.py
Détection d'anomalies (chute de conversion > 50%).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from data_pull import get_all_kpi_data
from common.metrics import stage_conversion_rate

ANOMALY_THRESHOLD_PCT = 50
MIN_DENOMINATOR = 20


def get_utc_now():
    try:
        from datetime import timezone
        return datetime.now(timezone.UTC)
    except AttributeError:
        return datetime.utcnow()


def check_anomalies(client_id: str):
    now = get_utc_now()
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    prev_end = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    prev_start = (now - timedelta(days=14)).strftime("%Y-%m-%d")

    data = get_all_kpi_data(client_id, start_date, end_date)
    prev_data = get_all_kpi_data(client_id, prev_start, prev_end)

    curr_rate = stage_conversion_rate(data["prev_stage_leads"], data["curr_stage_leads"])
    prev_rate = stage_conversion_rate(prev_data["prev_stage_leads"], prev_data["curr_stage_leads"])

    if prev_rate["value"] is not None and curr_rate["value"] is not None:
        if prev_rate["denominator"] >= MIN_DENOMINATOR and curr_rate["denominator"] >= MIN_DENOMINATOR:
            drop = ((prev_rate["value"] - curr_rate["value"]) / prev_rate["value"]) * 100
            if drop > ANOMALY_THRESHOLD_PCT:
                msg = f"🚨 Anomalie : Taux de conversion en chute de {drop:.1f}% !\n"
                msg += f"Actuel : {curr_rate['value']:.1f}% (basé sur {curr_rate['denominator']})\n"
                msg += f"Précédent : {prev_rate['value']:.1f}% (basé sur {prev_rate['denominator']})"
                return msg
    return None


if __name__ == "__main__":
    print(check_anomalies("client_test_123") or "✅ Aucune anomalie")
