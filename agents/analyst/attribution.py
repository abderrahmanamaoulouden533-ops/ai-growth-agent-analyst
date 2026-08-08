"""
attribution.py – Attribution des leads par source (campagne, ad set, asset)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.db import get_db_connection


def get_attribution_breakdown(client_id: str, start_date: str, end_date: str):
    """
    Retourne la répartition des leads par source (campagne).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            COALESCE(source, 'unattributed') as source,
            COUNT(*) as leads,
            COALESCE(SUM(contract_value), 0) as revenue
        FROM leads
        WHERE client_id = %s
          AND created_at::date BETWEEN %s::date AND %s::date
        GROUP BY source
        ORDER BY leads DESC
    """, (client_id, start_date, end_date))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    campaigns = {}
    for source, leads, revenue in rows:
        campaigns[source] = {"leads": leads, "revenue": float(revenue)}
    
    # Pour l'instant, on ne peut pas faire d'attribution par ad_set ou asset
    # car ces données ne sont pas encore dans la base. On retourne un dict vide.
    return {
        "campaigns": campaigns,
        "ad_sets": {},
        "assets": {}
    }


def get_top_performers(attribution_data):
    """
    Identifie la meilleure et la pire source (par CPL approximatif).
    """
    best = None
    worst = None
    best_cpl = float('inf')
    worst_cpl = 0.0
    
    for name, data in attribution_data["campaigns"].items():
        if data["leads"] > 0:
            # CPL approximatif = revenue / leads (ou on pourrait utiliser spend si disponible)
            cpl = data["revenue"] / data["leads"] if data["revenue"] > 0 else 0
            if cpl < best_cpl:
                best_cpl = cpl
                best = name
            if cpl > worst_cpl:
                worst_cpl = cpl
                worst = name
    
    return {
        "best": best,
        "best_cpl": best_cpl,
        "worst": worst,
        "worst_cpl": worst_cpl
    }


if __name__ == "__main__":
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    end = now.strftime("%Y-%m-%d")
    start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    
    data = get_attribution_breakdown("client_test_123", start, end)
    top = get_top_performers(data)
    
    print("📊 Attribution par source :")
    for source, d in data["campaigns"].items():
        print(f"  {source}: {d['leads']} leads, revenue: {d['revenue']:.2f}€")
    
    if top["best"]:
        print(f"\n🏆 Meilleure source : {top['best']} (CPL: {top['best_cpl']:.2f}€)")
    if top["worst"]:
        print(f"📉 Pire source : {top['worst']} (CPL: {top['worst_cpl']:.2f}€)")