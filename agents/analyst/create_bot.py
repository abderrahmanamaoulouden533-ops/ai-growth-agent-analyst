# create_bot.py – Script pour générer telegram_report.py avec un encodage UTF-8 propre

content = r'''"""
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

    message = "📊 *Rapport hebdomadaire - Agent Analyst*\n"
    message += f"📅 Période: {start_date} → {end_date}\n\n"
    message += "┌─────────────────────────\n"
    message += "│ *KPIs de performance*\n"
    message += "├─────────────────────────\n"
    message += format_kpi("CPL", metrics["cpl"], prev_metrics["cpl"]) + "\n"
    message += format_kpi("CPQ", metrics["cpq"], prev_metrics["cpq"]) + "\n"
    message += format_kpi("CPQL", metrics["cpql"], prev_metrics["cpql"]) + "\n"
    message += format_kpi("CPBD", metrics["cpbd"], prev_metrics["cpbd"]) + "\n"
    message += format_kpi("ROAS", metrics["roas"], prev_metrics["roas"]) + "\n"
    message += "\n"
    message += "├─────────────────────────\n"
    message += "│ *KPIs de conversion*\n"
    message += "├─────────────────────────\n"
    message += format_kpi("Taux conversion", metrics["stage_conversion"], prev_metrics["stage_conversion"]) + "\n"
    message += format_kpi("Temps 1er contact", metrics["time_to_first_contact"], prev_metrics["time_to_first_contact"]) + "\n"
    message += format_kpi("Taux réponse", metrics["response_rate"], prev_metrics["response_rate"]) + "\n"
    message += format_kpi("Taux présence", metrics["meeting_show_rate"], prev_metrics["meeting_show_rate"]) + "\n"
    message += "\n└─────────────────────────\n"
    message += f"🕐 Données du {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
    if kpi_explanation:
        message += f"\n📝 *Analyse LLM (CPL)* : {kpi_explanation}"
    if llm_recommendation:
        message += f"\n💡 *Recommandation LLM* : {llm_recommendation}"
    await update.message.reply_text(message, parse_mode='Markdown')


async def start(update, context):
    await update.message.reply_text(
        "👋 Bonjour ! Je suis l'Agent Analyst.\n"
        "📌 Commandes disponibles :\n"
        "/help - Afficher cette aide\n"
        "/health - Vérifier l'état du système\n"
        "/report - Rapport KPI hebdomadaire\n"
        "/weekly_report - Rapport d'optimisation complet\n"
        "/alerts - Vérifier les anomalies de conversion\n"
        "/observe - Lien vers les traces Langfuse",
        parse_mode=None
    )


async def help_command(update, context):
    await update.message.reply_text(
        "📋 Commandes de l'Agent Analyst :\n\n"
        "/start - Démarrer le bot\n"
        "/help - Afficher cette aide\n"
        "/health - Vérifier l'état du système\n"
        "/report - Afficher le rapport KPI hebdomadaire\n"
        "/weekly_report - Rapport d'optimisation (scale/pause/rewrite)\n"
        "/alerts - Détection d'anomalies (chutes de conversion)\n"
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
        "🩺 État de l'Agent Analyst :\n\n"
        f"{db_status}\n"
        f"{lf_status}\n"
        f"{llm_status}\n\n"
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
    await update.message.reply_text(f"🔍 Consultez les traces Langfuse :\n{langfuse_url}")


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

# Écrire le fichier avec l'encodage UTF-8
with open("telegram_report.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Fichier telegram_report.py créé avec succès (encodage UTF-8).")