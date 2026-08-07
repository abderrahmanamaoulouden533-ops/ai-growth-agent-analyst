"""
landing_pages.py – Suivi des performances des landing pages (B3)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from common.db import get_db_connection

THRESHOLD_CONVERSION_RATE = 15.0  # %


def get_landing_page_conversion_rates(client_id: str, start_date: str, end_date: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT page_url, 
               SUM(visitors) as total_visitors, 
               SUM(form_submissions) as total_submissions
        FROM landing_page_stats
        WHERE client_id = %s AND date BETWEEN %s AND %s
        GROUP BY page_url
    """, (client_id, start_date, end_date))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = []
    for page_url, visitors, submissions in rows:
        rate = (submissions / visitors * 100) if visitors > 0 else 0.0
        flagged = rate < THRESHOLD_CONVERSION_RATE
        results.append({
            "page_url": page_url,
            "visitors": visitors,
            "submissions": submissions,
            "conversion_rate": rate,
            "flagged": flagged,
            "threshold": THRESHOLD_CONVERSION_RATE
        })
    return results


def flag_underperforming_pages(client_id: str, start_date: str, end_date: str) -> list:
    results = get_landing_page_conversion_rates(client_id, start_date, end_date)
    return [r for r in results if r["flagged"]]


if __name__ == "__main__":
    now = datetime.utcnow()
    start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    flagged = flag_underperforming_pages("client_test_123", start, end)
    if flagged:
        print("🚨 Pages sous-performantes (<15%) :")
        for f in flagged:
            print(f"  - {f['page_url']} : {f['conversion_rate']:.1f}%")
    else:
        print("✅ Aucune page sous-performante (ou pas de données).")