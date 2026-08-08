"""
telegram_report.py
Bot Telegram complet pour l'Agent Analyst.
Commandes : /start, /help, /health, /report, /weekly_report, /alerts, /observe, /landing, /predict, /cohort, /scoring, /abtest
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Imports internes
from agents.analyst.data_pull import get_all_kpi_data
from common.metrics import get_all_metrics
from common.llm import generate_llm_response
from common.tracing import get_tracer
from common.db import get_db_connection
from common.logging import log_action

# --- Imports directs (sans try/except) ---
from agents.analyst.predictive_roas import run_prediction
from agents.analyst.cohort_analysis import run_cohort_analysis
from agents.analyst.scoring_feedback import run_scoring_feedback
from agents.analyst.ab_test_conclusions import run_ab_test_conclusion
from agents.analyst.weekly_report import generate_weekly_optimization
from agents.analyst.anomaly_detector import check_anomalies
from agents.analyst.landing_pages import flag_underperforming_pages
from agents.analyst.scheduler import start_scheduler

# Import du décorateur observe avec fallback
try:
    from langfuse import observe
except ImportError:
    def observe(*args, **kwargs):
        return lambda func: func
    print("⚠️ Langfuse non installé, décorateur observe désactivé")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("❌ Erreur : TELEGRAM_TOKEN non défini dans .env")
    exit(1)


# =========================================================================
# Fonctions utilitaires
# =========================================================================

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


def generate_kpi_explanation_simple(kpi_name, value, trend):
    return f"{kpi_name} est à {value:.2f} (tendance: {trend})"


# =========================================================================
# Handlers des commandes
# =========================================================================

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

    # Explication simple avec gestion de None
    kpi_explanation = ""
    if metrics["cpl"]["value"] is not None:
        if prev_metrics["cpl"]["value"] is not None:
            trend = "up" if metrics["cpl"]["value"] > prev_metrics["cpl"]["value"] else "down"
        else:
            trend = "stable"
        kpi_explanation = generate_kpi_explanation_simple("CPL", metrics["cpl"]["value"], trend)

    # Recommandation via LLM
    llm_recommendation = ""
    try:
        rec_prompt = f"""
Analyse ces KPIs marketing :
- CPL: {metrics['cpl']['value'] if metrics['cpl']['value'] is not None else 'N/A'}
- CPQL: {metrics['cpql']['value'] if metrics['cpql']['value'] is not None else 'N/A'}
- Taux de conversion: {metrics['stage_conversion']['value'] if metrics['stage_conversion']['value'] is not None else 'N/A'}%
- Taux de réponse: {metrics['response_rate']['value'] if metrics['response_rate']['value'] is not None else 'N/A'}%
Propose une recommandation concrète (1 phrase) pour améliorer la performance.
"""
        llm_recommendation = generate_llm_response(rec_prompt, system_prompt="Tu es un expert en marketing digital. Donne une recommandation courte et actionnable.")
    except Exception as e:
        print(f"⚠️ Erreur génération recommandation LLM: {e}")

    # Construction du message (texte brut)
    message = "📊 Rapport hebdomadaire - Agent Analyst\n"
    message += f"📅 Période: {start_date} → {end_date}\n\n"
    message += "┌─────────────────────────\n"
    message += "│ KPIs de performance\n"
    message += "├─────────────────────────\n"
    message += format_kpi("CPL", metrics["cpl"], prev_metrics["cpl"]) + "\n"
    message += format_kpi("CPQ", metrics["cpq"], prev_metrics["cpq"]) + "\n"
    message += format_kpi("CPQL", metrics["cpql"], prev_metrics["cpql"]) + "\n"
    message += format_kpi("CPBD", metrics["cpbd"], prev_metrics["cpbd"]) + "\n"
    message += format_kpi("ROAS", metrics["roas"], prev_metrics["roas"]) + "\n"
    message += "\n"
    message += "├─────────────────────────\n"
    message += "│ KPIs de conversion\n"
    message += "├─────────────────────────\n"
    message += format_kpi("Taux conversion", metrics["stage_conversion"], prev_metrics["stage_conversion"]) + "\n"
    message += format_kpi("Temps 1er contact", metrics["time_to_first_contact"], prev_metrics["time_to_first_contact"]) + "\n"
    message += format_kpi("Taux réponse", metrics["response_rate"], prev_metrics["response_rate"]) + "\n"
    message += format_kpi("Taux présence", metrics["meeting_show_rate"], prev_metrics["meeting_show_rate"]) + "\n"
    message += "\n└─────────────────────────\n"
    message += f"🕐 Données du {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
    if kpi_explanation:
        message += f"\n📝 Analyse KPI : {kpi_explanation}"
    if llm_recommendation:
        message += f"\n💡 Recommandation LLM : {llm_recommendation}"

    await update.message.reply_text(message, parse_mode=None)


async def start(update, context):
    await update.message.reply_text(
        "👋 Bonjour ! Je suis l'Agent Analyst.\n"
        "📌 Commandes disponibles :\n"
        "/help - Afficher cette aide\n"
        "/health - Vérifier l'état du système\n"
        "/report - Rapport KPI hebdomadaire\n"
        "/weekly_report - Rapport d'optimisation complet\n"
        "/alerts - Vérifier les anomalies de conversion\n"
        "/observe - Lien vers les traces Langfuse\n"
        "/landing - Pages sous-performantes (<15%)\n"
        "/predict - Prédiction ROAS 30 jours\n"
        "/cohort - Analyse des cohortes par source\n"
        "/scoring - Précision du modèle de scoring (Qualifier)\n"
        "/abtest - Conclusion du dernier A/B test",
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
        "/observe - Lien vers les traces Langfuse\n"
        "/landing - Afficher les pages avec conversion < 15%\n"
        "/predict - Prédiction des revenus sur 30 jours\n"
        "/cohort - Analyse des cohortes (taux de conversion par source)\n"
        "/scoring - Précision du modèle de scoring (Qualifier)\n"
        "/abtest - Conclusion du dernier A/B test",
        parse_mode=None
    )


async def health(update, context):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        db_status = "✅ PostgreSQL : OK"
    except Exception:
        db_status = "❌ PostgreSQL : Erreur de connexion"

    tracer = get_tracer()
    lf_status = "✅ Langfuse : OK" if tracer else "⚠️ Langfuse : non initialisé"

    try:
        from common.llm import get_llm
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
    try:
        report = generate_weekly_optimization("client_test_123")
        await update.message.reply_text(report, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Une erreur est survenue lors de la génération du rapport.")


async def alerts_command(update, context):
    try:
        alert = check_anomalies("client_test_123")
        if alert:
            await update.message.reply_text(f"🚨 {alert}")
        else:
            await update.message.reply_text("✅ Aucune anomalie détectée.")
    except Exception:
        await update.message.reply_text("❌ Une erreur est survenue lors de la détection des anomalies.")


async def observe_command(update, context):
    langfuse_url = "https://cloud.langfuse.com/project/agent-analyst/traces"
    await update.message.reply_text(f"🔍 Consultez les traces Langfuse :\n{langfuse_url}")


async def landing_command(update, context):
    client_id = "client_test_123"
    now = datetime.utcnow()
    end = now.strftime("%Y-%m-%d")
    start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    try:
        flagged = flag_underperforming_pages(client_id, start, end)
        if not flagged:
            await update.message.reply_text("✅ Aucune page sous-performante (<15%) détectée.")
            return
        msg = "🚨 *Pages avec conversion < 15% :*\n\n"
        for f in flagged:
            msg += f"📄 {f['page_url']}\n"
            msg += f"   Taux : {f['conversion_rate']:.1f}% (visiteurs: {f['visitors']}, conversions: {f['submissions']})\n"
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Une erreur est survenue lors de l'analyse des pages.")


# =========================================================================
# Handler /predict
# =========================================================================
async def predict_command(update, context):
    """Prédiction ROAS sur 30 jours."""
    try:
        result = run_prediction()
        if result['status'] == 'insufficient_data':
            await update.message.reply_text(f"⚠️ {result['message']}")
            return
        msg = f"📈 *Prédiction ROAS 30 jours*\n\n"
        msg += f"💰 Revenus estimés :\n"
        msg += f"   · Bas : {result['expected_revenue_range']['low']:.0f}€\n"
        msg += f"   · Haut : {result['expected_revenue_range']['high']:.0f}€\n\n"
        msg += f"📊 Pipeline : {result['assumptions']['total_pipeline']} leads\n"
        msg += f"🎯 Deals projetés : {result['assumptions']['projected_deals']:.1f}\n"
        msg += f"📌 Deal moyen : {result['assumptions']['avg_deal_value']:.0f}€"
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Une erreur est survenue lors de la prédiction.")


# =========================================================================
# Handler /cohort
# =========================================================================
async def cohort_command(update, context):
    """Analyse des cohortes."""
    try:
        result = run_cohort_analysis()
        if result["status"] == "no_data":
            await update.message.reply_text("⚠️ Aucune donnée de cohorte disponible.")
            return
        msg = "📊 *Analyse de cohortes*\n\n"
        msg += "Taux de conversion par source :\n"
        for source, data in result["summary"].items():
            msg += f"  • {source}: {data['conversion_rate']:.1f}% ({data['closed']}/{data['total']})\n"
        msg += f"\n🏆 *Meilleure source* : {result['best_source']} ({result['best_rate']:.1f}%)"
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Une erreur est survenue lors de l'analyse des cohortes.")


# =========================================================================
# Handler /scoring
# =========================================================================
async def scoring_command(update, context):
    """Affiche la précision du modèle de scoring (Qualifier)."""
    try:
        result = run_scoring_feedback()
        if result["status"] == "no_data":
            await update.message.reply_text("⚠️ Pas assez de données pour évaluer le scoring.")
            return
        msg = f"🎯 *Précision du modèle de scoring*\n\n"
        msg += f"📊 F1-score : {result['f1']:.2f}\n"
        msg += f"🎯 Précision : {result['precision']:.2f}\n"
        msg += f"📈 Rappel : {result['recall']:.2f}\n"
        msg += f"📌 Échantillons : {result['samples']}"
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Une erreur est survenue lors de l'évaluation du scoring.")


# =========================================================================
# Handler /abtest
# =========================================================================
async def abtest_command(update, context):
    """Affiche la conclusion du dernier A/B test."""
    try:
        result = run_ab_test_conclusion(test_id="test_1")
        if result["status"] == "insufficient_data":
            await update.message.reply_text(f"⚠️ Données insuffisantes : {result.get('message', '')}")
            return
        msg = f"📊 *Conclusion A/B Test*\n\n"
        if result["status"] == "winner_declared":
            msg += f"🏆 *Gagnant* : {result['winner']}\n"
            msg += f"📈 Taux de conversion : {result['winner_rate']:.2%}\n"
            msg += f"📊 p-value : {result['p_value']:.4f}\n"
            msg += f"✅ Significatif (p < 0.05)"
        else:
            msg += f"❌ *Aucun gagnant déclaré*\n"
            msg += f"📈 Meilleur taux : {result['best_rate']:.2%}\n"
            msg += f"📊 p-value : {result['p_value']:.4f}\n"
            msg += f"⚠️ Pas de différence significative"
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Une erreur est survenue lors de l'analyse du test A/B.")


# =========================================================================
# Point d'entrée
# =========================================================================

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("weekly_report", weekly_report_command))
    app.add_handler(CommandHandler("alerts", alerts_command))
    app.add_handler(CommandHandler("observe", observe_command))
    app.add_handler(CommandHandler("landing", landing_command))
    app.add_handler(CommandHandler("predict", predict_command))
    app.add_handler(CommandHandler("cohort", cohort_command))
    app.add_handler(CommandHandler("scoring", scoring_command))
    app.add_handler(CommandHandler("abtest", abtest_command))

    # Démarrer le scheduler
    start_scheduler()

    print("🤖 Agent Analyst bot démarré. Envoyez /help pour la liste des commandes.")
    app.run_polling()


if __name__ == "__main__":
    main()