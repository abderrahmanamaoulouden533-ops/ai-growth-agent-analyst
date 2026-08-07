"""
weekly_report.py
Génère un rapport d'optimisation hebdomadaire.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from agents.analyst.data_pull import get_all_kpi_data
from common.metrics import cpl, cpql          # <-- IMPORT AJOUTÉ
from common.llm import generate_llm_response


def get_utc_now():
    try:
        from datetime import timezone
        return datetime.now(timezone.UTC)
    except AttributeError:
        return datetime.utcnow()


def generate_weekly_optimization(client_id: str) -> str:
    now = get_utc_now()
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    data = get_all_kpi_data(client_id, start_date, end_date)
    cpl_result = cpl(data["ad_spend"], data["submissions"])
    cpql_result = cpql(data["ad_spend"], data["leads_ge_61"])

    recommendations = []
    if cpl_result["value"] is not None and cpl_result["value"] > 100:
        recommendations.append("🔴 Réduire le budget sur les campagnes à faible performance (CPL > 100€)")
    if data["submissions"] < 50:
        recommendations.append("🔵 Augmenter le budget des campagnes à fort CTR")
    if data["appointments"] < 5:
        recommendations.append("🟠 Améliorer la prise de rendez-vous")
    if not recommendations:
        recommendations.append("✅ Aucune action urgente recommandée.")

    report = f"📋 *Rapport d'optimisation - Semaine du {start_date}*\n\n"
    report += f"💰 Dépenses totales : {data['ad_spend']:.2f} €\n"
    report += f"📥 Leads générés : {data['submissions']}\n"
    if cpl_result["value"] is not None:
        report += f"📊 CPL moyen : {cpl_result['value']:.2f} €\n"
    if cpql_result["value"] is not None:
        report += f"🎯 CPQL : {cpql_result['value']:.2f} €\n"
    report += "\n---\n*Recommandations :*\n"
    report += "\n".join(f"- {r}" for r in recommendations)

    # Générer une recommandation LLM
    llm_rec = ""
    try:
        rec_prompt = f"""
Analyse ces KPIs marketing :
- CPL: {cpl_result['value'] if cpl_result['value'] is not None else 'N/A'}
- CPQL: {cpql_result['value'] if cpql_result['value'] is not None else 'N/A'}
- Leads: {data['submissions']}
- Rendez-vous: {data['appointments']}
Propose une recommandation courte pour améliorer la performance.
"""
        llm_rec = generate_llm_response(rec_prompt, system_prompt="Tu es un expert en marketing digital. Donne une recommandation courte et actionnable.")
    except Exception as e:
        print(f"⚠️ Erreur génération recommandation LLM: {e}")

    if llm_rec:
        report += f"\n🤖 *Recommandation LLM* : {llm_rec}"
    return report


if __name__ == "__main__":
    print(generate_weekly_optimization("client_test_123"))