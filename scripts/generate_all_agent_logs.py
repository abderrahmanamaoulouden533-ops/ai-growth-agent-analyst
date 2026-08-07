"""
scripts/generate_all_agent_logs.py
Génère des logs simulés pour les 7 agents du système.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logging import log_action

def generate_logs_for_all_agents():
    agents = [
        ("commander", "route_task"),
        ("crm_keeper", "create_lead"),
        ("qualifier", "score_lead"),
        ("content_strategist", "generate_copy"),
        ("media_buyer", "allocate_budget"),
        ("closer", "send_message"),
        ("analyst", "compute_kpis")
    ]

    for agent_name, action in agents:
        log_action(
            agent_name=agent_name,
            action_type=action,
            input_summary=f"Simulation pour {agent_name}",
            output_summary=f"Résultat simulé pour {agent_name}",
            client_id="client_test_123",
            lead_id="ld_001",
            model_used="rule-based",
            latency_ms=100
        )
        print(f"✅ Log généré pour {agent_name}")

    print("\n🎉 Tous les logs ont été générés dans ~/logs/")

if __name__ == "__main__":
    generate_logs_for_all_agents()