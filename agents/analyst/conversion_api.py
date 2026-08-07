"""
conversion_api.py – Conversion API Push (C1)
Envoie les deals closed_won au Media Buyer pour push vers Meta/Google.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import httpx
from datetime import datetime, timedelta
from common.db import get_db_connection
from common.logging import log_action

MEDIA_BUYER_URL = os.getenv("MEDIA_BUYER_URL", "https://media.aphelionxcore.com")


def get_closed_won_deals(client_id: str, days: int = 7):
    """Récupère les deals closed_won avec leurs click_ids."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT lead_id, click_id, click_id_platform, contract_value,
               first_name, last_name, email
        FROM leads
        WHERE client_id = %s
          AND lead_stage = 'closed_won'
          AND created_at > NOW() - (%s * INTERVAL '1 DAY')
    """, (client_id, days))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def push_conversion_to_media_buyer(deal_data: dict, dry_run: bool = True) -> bool:
    """
    Envoie un deal au Media Buyer pour Conversion API.
    Si dry_run=True, on simule l'envoi sans faire la requête HTTP.
    """
    payload = {
        "client_id": deal_data["client_id"],
        "click_id": deal_data["click_id"],
        "platform": deal_data.get("click_id_platform", "meta"),
        "conversion_value": deal_data["contract_value"],
        "email": deal_data["email"]
    }

    if dry_run:
        print(f"🔬 [DRY RUN] Envoi simulé de {payload}")
        return True

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{MEDIA_BUYER_URL}/crm/push-segment",
                json=payload
            )
            return resp.status_code == 200
    except Exception as e:
        print(f"⚠️ Erreur push conversion: {e}")
        return False


def run_conversion_push(client_id: str = "client_test_123", dry_run: bool = True):
    """
    Job hebdomadaire : compile et envoie tous les closed_won.
    dry_run=True : mode simulation (ne fait pas de vraies requêtes).
    """
    deals = get_closed_won_deals(client_id)
    print(f"📊 {len(deals)} deals closed_won trouvés")

    success_count = 0
    for deal in deals:
        deal_data = {
            "client_id": client_id,
            "lead_id": deal[0],
            "click_id": deal[1],
            "click_id_platform": deal[2],
            "contract_value": deal[3],
            "first_name": deal[4],
            "last_name": deal[5],
            "email": deal[6]
        }
        if push_conversion_to_media_buyer(deal_data, dry_run=dry_run):
            success_count += 1
        else:
            print(f"⚠️ Échec pour lead {deal[0]}")

    log_action(
        agent_name="analyst",
        action_type="conversion_api_push",
        input_summary=f"{len(deals)} deals traités, dry_run={dry_run}",
        output_summary=f"{success_count} poussés avec succès",
        client_id=client_id,
        model_used="rule-based"
    )
    print(f"✅ {success_count}/{len(deals)} deals poussés (dry_run={dry_run})")


if __name__ == "__main__":
    run_conversion_push(dry_run=True)