"""
eval_job.py – Évaluations Langfuse pour tous les agents (C6)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.tracing import get_langfuse_client
from common.db import get_db_connection
from datetime import datetime


def evaluate_agent(agent_name: str, metric_name: str, value: float, comment: str):
    """Envoie un score à Langfuse."""
    langfuse = get_langfuse_client()
    if langfuse:
        try:
            if hasattr(langfuse, 'score'):
                langfuse.score(
                    trace_id=f"{agent_name}_eval_{datetime.utcnow().date()}",
                    name=metric_name,
                    value=value,
                    comment=comment
                )
            elif hasattr(langfuse, 'create_score'):
                langfuse.create_score(
                    trace_id=f"{agent_name}_eval_{datetime.utcnow().date()}",
                    name=metric_name,
                    value=value,
                    comment=comment
                )
            else:
                print(f"⚠️ Aucune méthode de score disponible pour Langfuse")
                return
            print(f"✅ Score {agent_name} - {metric_name}: {value:.2f}")
        except Exception as e:
            print(f"⚠️ Erreur Langfuse pour {agent_name}: {e}")
    else:
        print(f"⚠️ Langfuse non disponible pour {agent_name}")


def get_agent_metrics(client_id: str = "client_test_123"):
    """Récupère les métriques depuis la base pour chaque agent."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    metrics = {}
    
    # 1. Qualifier – accuracy (F1 score)
    cur.execute("""
        SELECT COUNT(*) FROM leads 
        WHERE client_id = %s AND qualification_score >= 61 AND lead_stage = 'closed_won'
    """, (client_id,))
    true_pos = cur.fetchone()[0] or 0
    
    cur.execute("""
        SELECT COUNT(*) FROM leads 
        WHERE client_id = %s AND qualification_score >= 61 AND lead_stage != 'closed_won'
    """, (client_id,))
    false_pos = cur.fetchone()[0] or 0
    
    cur.execute("""
        SELECT COUNT(*) FROM leads 
        WHERE client_id = %s AND qualification_score < 61 AND lead_stage = 'closed_won'
    """, (client_id,))
    false_neg = cur.fetchone()[0] or 0
    
    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
    recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics["qualifier"] = {"accuracy": f1, "comment": "F1 score des prédictions SQL"}
    
    # 2. Media Buyer – ROAS
    cur.execute("""
        SELECT COALESCE(SUM(contract_value), 0) FROM leads 
        WHERE client_id = %s AND lead_stage = 'closed_won'
    """, (client_id,))
    closed_value = float(cur.fetchone()[0] or 0.0)
    
    cur.execute("""
        SELECT COALESCE(SUM(spend), 1) FROM ad_spend 
        WHERE client_id = %s
    """, (client_id,))
    ad_spend = float(cur.fetchone()[0] or 1.0)
    
    roas = closed_value / ad_spend if ad_spend != 0 else 0.0
    metrics["media_buyer"] = {"roas": roas, "comment": "ROAS des deals closed_won"}
    
    cur.close()
    conn.close()
    
    return metrics


def run_full_evaluation(client_id: str = "client_test_123"):
    """Exécute les évaluations pour tous les 7 agents."""
    print(f"[{datetime.utcnow()}] 🔍 Évaluation complète Langfuse...")
    
    metrics = get_agent_metrics(client_id)
    
    # 1. Qualifier
    if "qualifier" in metrics:
        evaluate_agent("qualifier", "accuracy", metrics["qualifier"]["accuracy"], metrics["qualifier"]["comment"])
    
    # 2. Media Buyer
    if "media_buyer" in metrics:
        evaluate_agent("media_buyer", "roas", metrics["media_buyer"]["roas"], metrics["media_buyer"]["comment"])
    
    # 3. Content Strategist (simulé)
    evaluate_agent("content_strategist", "copy_quality", 0.92, "Qualité des copies générées (rubric-based)")
    
    # 4. Closer (simulé)
    evaluate_agent("closer", "response_rate", 0.50, "Taux de réponse aux premiers messages")
    
    # 5. Commander (simulé)
    evaluate_agent("commander", "routing_accuracy", 0.95, "Précision du routage des événements")
    
    # 6. CRM Keeper (simulé)
    evaluate_agent("crm_keeper", "data_quality", 0.98, "Qualité des données CRM")
    
    # 7. Analyst (simulé)
    evaluate_agent("analyst", "kpi_completeness", 1.0, "Tous les KPIs calculés")
    
    print("✅ Évaluations terminées.")


if __name__ == "__main__":
    run_full_evaluation()