"""
scheduler.py – Planification des tâches automatiques (APScheduler)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

# Jobs existants
from agents.analyst.weekly_report import generate_weekly_optimization
from agents.analyst.conversion_api import run_conversion_push
from agents.analyst.predictive_roas import run_prediction
from agents.analyst.cohort_analysis import run_cohort_analysis
from agents.analyst.scoring_feedback import run_scoring_feedback
from agents.analyst.ab_test_conclusions import run_ab_test_conclusion
from agents.analyst.eval_job import run_full_evaluation


def weekly_optimization_job():
    print(f"[{datetime.utcnow()}] 🔔 Exécution du rapport d'optimisation hebdomadaire...")
    report = generate_weekly_optimization("client_test_123")
    print(report)
    print("✅ Rapport généré.\n")


def start_scheduler():
    scheduler = BackgroundScheduler()

    # Job 1 – Rapport d'optimisation (tous les lundis à 09:00)
    scheduler.add_job(
        weekly_optimization_job,
        trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
        id='weekly_optimization',
        replace_existing=True
    )
    print("⏰ Rapport d'optimisation planifié (tous les lundis à 09:00).")

    # Job 2 – Conversion API push (tous les mercredis à 09:00)
    scheduler.add_job(
        run_conversion_push,
        trigger=CronTrigger(day_of_week='wed', hour=9, minute=0),
        id='conversion_push',
        replace_existing=True,
        kwargs={'dry_run': True}
    )
    print("📤 Conversion API push planifiée (tous les mercredis à 09:00, dry_run=True).")

    # Job 3 – Prédiction ROAS (tous les dimanches à 08:00)
    scheduler.add_job(
        run_prediction,
        trigger=CronTrigger(day_of_week='sun', hour=8, minute=0),
        id='predictive_roas',
        replace_existing=True
    )
    print("📈 Prédiction ROAS planifiée (tous les dimanches à 08:00).")

    # Job 4 – Cohort Analysis (tous les mardis à 08:00)
    scheduler.add_job(
        run_cohort_analysis,
        trigger=CronTrigger(day_of_week='tue', hour=8, minute=0),
        id='cohort_analysis',
        replace_existing=True
    )
    print("📊 Cohort analysis planifiée (tous les mardis à 08:00).")

    # Job 5 – Scoring Feedback (tous les jeudis à 08:00)
    scheduler.add_job(
        run_scoring_feedback,
        trigger=CronTrigger(day_of_week='thu', hour=8, minute=0),
        id='scoring_feedback',
        replace_existing=True
    )
    print("🎯 Scoring feedback planifié (tous les jeudis à 08:00).")

    # Job 6 – A/B Test Conclusions (tous les vendredis à 08:00)
    scheduler.add_job(
        run_ab_test_conclusion,
        trigger=CronTrigger(day_of_week='fri', hour=8, minute=0),
        id='ab_test_conclusion',
        replace_existing=True
    )
    print("📊 A/B test conclusions planifiées (tous les vendredis à 08:00).")

    # Job 7 – Langfuse Full Evaluation (tous les samedis à 09:00)
    scheduler.add_job(
        run_full_evaluation,
        trigger=CronTrigger(day_of_week='sat', hour=9, minute=0),
        id='langfuse_full_eval',
        replace_existing=True
    )
    print("🔍 Langfuse full eval planifiée (tous les samedis à 09:00).")

    scheduler.start()
    print("⏰ Scheduler démarré.")
    return scheduler


if __name__ == "__main__":
    # Exécution manuelle pour tester
    print("🧪 Test manuel des jobs...\n")
    weekly_optimization_job()
    run_conversion_push(dry_run=True)
    run_prediction()
    run_cohort_analysis()
    run_scoring_feedback()
    run_ab_test_conclusion()
    run_full_evaluation()
    print("\n✅ Tous les jobs ont été testés.")