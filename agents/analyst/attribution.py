"""
attribution.py
Décomposition des leads par source.
"""

def get_attribution_breakdown(client_id, start_date, end_date):
    return {
        "campaigns": {
            "campaign_1": {"leads": 30, "spend": 500},
            "campaign_2": {"leads": 20, "spend": 300}
        },
        "ad_sets": {
            "adset_1": {"leads": 25, "spend": 400},
            "adset_2": {"leads": 15, "spend": 200}
        },
        "assets": {
            "asset_1": {"leads": 20, "spend": 350},
            "asset_2": {"leads": 10, "spend": 150}
        }
    }

def get_top_performers(data):
    best = worst = None
    best_cpl = float('inf')
    worst_cpl = 0
    for name, d in data["campaigns"].items():
        if d["spend"] > 0 and d["leads"] > 0:
            cpl = d["spend"] / d["leads"]
            if cpl < best_cpl:
                best_cpl = cpl; best = name
            if cpl > worst_cpl:
                worst_cpl = cpl; worst = name
    return {"best": best, "best_cpl": best_cpl, "worst": worst, "worst_cpl": worst_cpl}

if __name__ == "__main__":
    data = get_attribution_breakdown("", "", "")
    top = get_top_performers(data)
    print(f"🏆 Meilleure campagne : {top['best']} (CPL: {top['best_cpl']:.2f}€)")
    print(f"📉 Pire : {top['worst']} (CPL: {top['worst_cpl']:.2f}€)")