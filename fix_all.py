import os
import sys

# ========================
# 1. Recréer common/__init__.py
# ========================
with open("common/__init__.py", "w", encoding="utf-8") as f:
    f.write("")

# ========================
# 2. Recréer common/metrics.py (version propre)
# ========================
metrics_content = '''"""
common/metrics.py
Module central de calcul des KPIs – fonctions pures uniquement.
"""

from typing import Dict, Any
from datetime import datetime
import math


def cpl(total_ad_spend: float, total_form_submissions: int) -> Dict[str, Any]:
    if total_form_submissions == 0:
        return {"value": None, "numerator": total_ad_spend, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_ad_spend / total_form_submissions,
        "numerator": total_ad_spend,
        "denominator": total_form_submissions,
        "data_as_of": datetime.utcnow().isoformat()
    }


def cpq(total_ad_spend: float, leads_with_score_ge_31: int) -> Dict[str, Any]:
    if leads_with_score_ge_31 == 0:
        return {"value": None, "numerator": total_ad_spend, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_ad_spend / leads_with_score_ge_31,
        "numerator": total_ad_spend,
        "denominator": leads_with_score_ge_31,
        "data_as_of": datetime.utcnow().isoformat()
    }


def cpql(total_ad_spend: float, leads_with_score_ge_61: int) -> Dict[str, Any]:
    if leads_with_score_ge_61 == 0:
        return {"value": None, "numerator": total_ad_spend, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_ad_spend / leads_with_score_ge_61,
        "numerator": total_ad_spend,
        "denominator": leads_with_score_ge_61,
        "data_as_of": datetime.utcnow().isoformat()
    }


def cpbd(total_ad_spend: float, appointments_booked: int) -> Dict[str, Any]:
    if appointments_booked == 0:
        return {"value": None, "numerator": total_ad_spend, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_ad_spend / appointments_booked,
        "numerator": total_ad_spend,
        "denominator": appointments_booked,
        "data_as_of": datetime.utcnow().isoformat()
    }


def roas(total_contract_value_closed_won: float, total_ad_spend: float) -> Dict[str, Any]:
    if total_ad_spend == 0:
        return {"value": None, "numerator": total_contract_value_closed_won, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_contract_value_closed_won / total_ad_spend,
        "numerator": total_contract_value_closed_won,
        "denominator": total_ad_spend,
        "data_as_of": datetime.utcnow().isoformat()
    }


def stage_conversion_rate(leads_in_previous_stage: int, leads_in_current_stage: int) -> Dict[str, Any]:
    if leads_in_previous_stage == 0:
        return {"value": None, "numerator": leads_in_current_stage, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": (leads_in_current_stage / leads_in_previous_stage) * 100,
        "numerator": leads_in_current_stage,
        "denominator": leads_in_previous_stage,
        "data_as_of": datetime.utcnow().isoformat()
    }


def time_to_first_contact(total_minutes: float, number_of_contacts: int) -> Dict[str, Any]:
    if number_of_contacts == 0:
        return {"value": None, "numerator": total_minutes, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_minutes / number_of_contacts,
        "numerator": total_minutes,
        "denominator": number_of_contacts,
        "data_as_of": datetime.utcnow().isoformat()
    }


def response_rate(replied_first_contacts: int, total_first_contacts: int) -> Dict[str, Any]:
    if total_first_contacts == 0:
        return {"value": None, "numerator": replied_first_contacts, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": (replied_first_contacts / total_first_contacts) * 100,
        "numerator": replied_first_contacts,
        "denominator": total_first_contacts,
        "data_as_of": datetime.utcnow().isoformat()
    }


def meeting_show_rate(leads_showed_up: int, total_meetings_booked: int) -> Dict[str, Any]:
    if total_meetings_booked == 0:
        return {"value": None, "numerator": leads_showed_up, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": (leads_showed_up / total_meetings_booked) * 100,
        "numerator": leads_showed_up,
        "denominator": total_meetings_booked,
        "data_as_of": datetime.utcnow().isoformat()
    }


def get_all_metrics(data: dict) -> dict:
    return {
        "cpl": cpl(data["ad_spend"], data["submissions"]),
        "cpq": cpq(data["ad_spend"], data["leads_ge_31"]),
        "cpql": cpql(data["ad_spend"], data["leads_ge_61"]),
        "cpbd": cpbd(data["ad_spend"], data["appointments"]),
        "roas": roas(data["closed_won_value"], data["ad_spend"]),
        "stage_conversion": stage_conversion_rate(data["prev_stage_leads"], data["curr_stage_leads"]),
        "time_to_first_contact": time_to_first_contact(data["total_minutes_contact"], data["contacts_count"]),
        "response_rate": response_rate(data["replied_first_contacts"], data["total_first_contacts"]),
        "meeting_show_rate": meeting_show_rate(data["showed_up"], data["total_meetings"])
    }
'''

with open("common/metrics.py", "w", encoding="utf-8") as f:
    f.write(metrics_content)

print("✅ common/metrics.py recréé")

# ========================
# 3. Recréer analyst/weekly_report.py avec sys.path
# ========================
weekly_content = '''"""
weekly_report.py
Génère un rapport d'optimisation hebdomadaire.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from data_pull import get_all_kpi_data
from common.metrics import cpl, cpql
from llm_analyst import generate_optimization_recommendation


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

    report = f"📋 *Rapport d'optimisation - Semaine du {start_date}*\\n\\n"
    report += f"💰 Dépenses totales : {data['ad_spend']:.2f} €\\n"
    report += f"📥 Leads générés : {data['submissions']}\\n"
    if cpl_result["value"] is not None:
        report += f"📊 CPL moyen : {cpl_result['value']:.2f} €\\n"
    if cpql_result["value"] is not None:
        report += f"🎯 CPQL : {cpql_result['value']:.2f} €\\n"
    report += "\\n---\\n*Recommandations :*\\n"
    report += "\\n".join(f"- {r}" for r in recommendations)

    metrics_data = {
        "cpl": {"value": cpl_result["value"]},
        "cpql": {"value": cpql_result["value"]},
        "stage_conversion": {"value": None},
        "response_rate": {"value": None}
    }
    llm_rec = generate_optimization_recommendation(metrics_data)
    if llm_rec:
        report += f"\\n🤖 *Recommandation LLM* : {llm_rec}"
    return report


if __name__ == "__main__":
    print(generate_weekly_optimization("client_test_123"))
'''

with open("analyst/weekly_report.py", "w", encoding="utf-8") as f:
    f.write(weekly_content)
print("✅ analyst/weekly_report.py recréé")

# ========================
# 4. Recréer analyst/anomaly_detector.py avec sys.path
# ========================
anomaly_content = '''"""
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
                msg = f"🚨 Anomalie : Taux de conversion en chute de {drop:.1f}% !\\n"
                msg += f"Actuel : {curr_rate['value']:.1f}% (basé sur {curr_rate['denominator']})\\n"
                msg += f"Précédent : {prev_rate['value']:.1f}% (basé sur {prev_rate['denominator']})"
                return msg
    return None


if __name__ == "__main__":
    print(check_anomalies("client_test_123") or "✅ Aucune anomalie")
'''

with open("analyst/anomaly_detector.py", "w", encoding="utf-8") as f:
    f.write(anomaly_content)
print("✅ analyst/anomaly_detector.py recréé")

# ========================
# 5. Recréer analyst/telegram_report.py avec sys.path (version complète)
# ========================
telegram_content = '''"""
telegram_report.py
Bot Telegram complet pour l'Agent Analyst.
Commandes : /start, /help, /health, /report, /weekly_report, /alerts, /observe
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

from data_pull import get_all_kpi_data
from common.metrics import get_all_metrics
from langfuse_client import get_langfuse
from langfuse import observe

try:
    from weekly_report import generate_weekly_optimization
except ImportError:
    generate_weekly_optimization = None

try:
    from anomaly_detector import check_anomalies
except ImportError:
    check_anomalies = None

try:
    from llm_analyst import generate_kpi_explanation, generate_optimization_recommendation
except ImportError:
    generate_kpi_explanation = None
    generate_optimization_recommendation = None

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("❌ Erreur : TELEGRAM_TOKEN non défini dans .env")
    exit(1)


def format_kpi(name, result, previous_result=None):
    if result["value"] is None:
        return f"*{name}*: Pas de données"
    value = result["value"]
    if isinstance(value, float):
        formatted = f"{value:.2f} €" if value > 100 else f"{value:.1f}%"
    else:
        formatted = str(value)
    line = f"*{name}*: {formatted}"
    if previous_result and previous_result.get("value") is not None:
        try:
            delta = ((result["value"] - previous_result["value"]) / previous_result["value"]) * 100
            delta_symbol = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
            line += f" ({delta_symbol} {delta:+.1f}%)"
        except:
            pass
    if result.get("numerator") is not None and result.get("denominator") is not None:
        line += f"  *(basé sur {result['numerator']} / {result['denominator']})*"
    return line


def safe_llm_call(func, *args, **kwargs):
    if func is None:
        return None
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"⚠️ Erreur LLM: {e}")
        return None


@observe(name="analyst_weekly_report", as_type="generation")
async def report(update, context):
    client_id = "client_test_123"
    now = datetime.utcnow()
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    data = get_all_kpi_data(client_id, start_date, end_date)
    prev_data = get_all_kpi_data(client_id, (now - timedelta(days=14)).strftime("%Y-%m-%d"), (now - timedelta(days=7)).strftime("%Y-%m-%d"))
    metrics = get_all_metrics(data)
    prev_metrics = get_all_metrics(prev_data)

    kpi_explanation = ""
    if generate_kpi_explanation and metrics["cpl"]["value"] is not None:
        trend = "up" if metrics["cpl"]["value"] > prev_metrics["cpl"]["value"] else "down"
        kpi_explanation = safe_llm_call(generate_kpi_explanation, "CPL", metrics["cpl"]["value"], trend) or ""

    llm_recommendation = ""
    if generate_optimization_recommendation:
        rec_data = {
            "cpl": {"value": metrics["cpl"]["value"]},
            "cpql": {"value": metrics["cpql"]["value"]},
            "stage_conversion": {"value": metrics["stage_conversion"]["value"]},
            "response_rate": {"value": metrics["response_rate"]["value"]}
        }
        llm_recommendation = safe_llm_call(generate_optimization_recommendation, rec_data) or ""

    message = "📊 *Rapport hebdomadaire - Agent Analyst*\\n"
    message += f"📅 Période: {start_date} → {end_date}\\n\\n"
    message += "┌─────────────────────────\\n"
    message += "│ *KPIs de performance*\\n"
    message += "├─────────────────────────\\n"
    message += format_kpi("CPL", metrics["cpl"], prev_metrics["cpl"]) + "\\n"
    message += format_kpi("CPQ", metrics["cpq"], prev_metrics["cpq"]) + "\\n"
    message += format_kpi("CPQL", metrics["cpql"], prev_metrics["cpql"]) + "\\n"
    message += format_kpi("CPBD", metrics["cpbd"], prev_metrics["cpbd"]) + "\\n"
    message += format_kpi("ROAS", metrics["roas"], prev_metrics["roas"]) + "\\n"
    message += "\\n"
    message += "├─────────────────────────\\n"
    message += "│ *KPIs de conversion*\\n"
    message += "├─────────────────────────\\n"
    message += format_kpi("Taux conversion", metrics["stage_conversion"], prev_metrics["stage_conversion"]) + "\\n"
    message += format_kpi("Temps 1er contact", metrics["time_to_first_contact"], prev_metrics["time_to_first_contact"]) + "\\n"
    message += format_kpi("Taux réponse", metrics["response_rate"], prev_metrics["response_rate"]) + "\\n"
    message += format_kpi("Taux présence", metrics["meeting_show_rate"], prev_metrics["meeting_show_rate"]) + "\\n"
    message += "\\n└─────────────────────────\\n"
    message += f"🕐 Données du {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
    if kpi_explanation:
        message += f"\\n📝 *Analyse LLM (CPL)* : {kpi_explanation}"
    if llm_recommendation:
        message += f"\\n💡 *Recommandation LLM* : {llm_recommendation}"
    await update.message.reply_text(message, parse_mode='Markdown')


async def start(update, context):
    await update.message.reply_text(
        "👋 Bonjour ! Je suis l'Agent Analyst.\\n"
        "📌 Commandes disponibles :\\n"
        "/help - Afficher cette aide\\n"
        "/health - Vérifier l'état du système\\n"
        "/report - Rapport KPI hebdomadaire\\n"
        "/weekly_report - Rapport d'optimisation complet\\n"
        "/alerts - Vérifier les anomalies de conversion\\n"
        "/observe - Lien vers les traces Langfuse",
        parse_mode=None
    )


async def help_command(update, context):
    await update.message.reply_text(
        "📋 Commandes de l'Agent Analyst :\\n\\n"
        "/start - Démarrer le bot\\n"
        "/help - Afficher cette aide\\n"
        "/health - Vérifier l'état du système\\n"
        "/report - Afficher le rapport KPI hebdomadaire\\n"
        "/weekly_report - Rapport d'optimisation (scale/pause/rewrite)\\n"
        "/alerts - Détection d'anomalies (chutes de conversion)\\n"
        "/observe - Lien vers les traces Langfuse",
        parse_mode=None
    )


async def health(update, context):
    try:
        from data_pull import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        db_status = "✅ PostgreSQL : OK"
    except Exception as e:
        db_status = f"❌ PostgreSQL : {e}"

    langfuse = get_langfuse()
    lf_status = "✅ Langfuse : OK" if langfuse else "⚠️ Langfuse : non initialisé"

    try:
        from llm_analyst import get_llm
        llm = get_llm()
        llm_status = "✅ LLM (OpenRouter) : OK" if llm else "⚠️ LLM : non disponible"
    except:
        llm_status = "⚠️ LLM : erreur de chargement"

    message = (
        "🩺 État de l'Agent Analyst :\\n\\n"
        f"{db_status}\\n"
        f"{lf_status}\\n"
        f"{llm_status}\\n\\n"
        f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
    )
    await update.message.reply_text(message, parse_mode=None)


async def weekly_report_command(update, context):
    if generate_weekly_optimization is None:
        await update.message.reply_text("❌ Module weekly_report non disponible.")
        return
    try:
        report = generate_weekly_optimization("client_test_123")
        await update.message.reply_text(report, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur : {e}")


async def alerts_command(update, context):
    if check_anomalies is None:
        await update.message.reply_text("❌ Module anomaly_detector non disponible.")
        return
    try:
        alert = check_anomalies("client_test_123")
        if alert:
            await update.message.reply_text(f"🚨 {alert}")
        else:
            await update.message.reply_text("✅ Aucune anomalie détectée.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur : {e}")


async def observe_command(update, context):
    langfuse_url = "https://cloud.langfuse.com/project/agent-analyst/traces"
    await update.message.reply_text(f"🔍 Consultez les traces Langfuse :\\n{langfuse_url}")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("weekly_report", weekly_report_command))
    app.add_handler(CommandHandler("alerts", alerts_command))
    app.add_handler(CommandHandler("observe", observe_command))
    print("🤖 Agent Analyst bot démarré. Envoyez /help pour la liste des commandes.")
    app.run_polling()


if __name__ == "__main__":
    main()
'''

with open("analyst/telegram_report.py", "w", encoding="utf-8") as f:
    f.write(telegram_content)
print("✅ analyst/telegram_report.py recréé")

# ========================
# 6. Installer les dépendances manquantes
# ========================
print("Installation des dépendances...")
os.system("uv pip install psycopg2-binary python-dotenv python-telegram-bot langfuse litellm apscheduler fastapi uvicorn pydantic pytest tenacity httpx")

print("✅ Toutes les réparations sont effectuées.")
print("Vous pouvez maintenant lancer le bot avec :")
print("cd analyst && python telegram_report.py")