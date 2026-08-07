import sys
import os
# Ajouter le dossier common/ au chemin d'import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from logger import log_action

print("Génération des logs de test...")
# ... le reste du code reste identique

# Simuler une action du Commander
log_action(
    agent_name="commander",
    action_type="route_task",
    input_summary="Received 'new lead' via Telegram",
    output_summary="Routed to Qualifier webhook",
    client_id="client_test_123",
    lead_id="ld_001",
    latency_ms=42
)

# Simuler une action du CRM Keeper
log_action(
    agent_name="crm_keeper",
    action_type="create_lead",
    input_summary="Lead data from form",
    output_summary="Lead created with ID ld_002",
    client_id="client_test_123",
    lead_id="ld_002",
    latency_ms=120
)

# Simuler une action du Qualifier
log_action(
    agent_name="qualifier",
    action_type="score_lead",
    input_summary="Lead profile JSON",
    output_summary="Score 85 - SQL",
    client_id="client_test_123",
    lead_id="ld_001",
    model_used="deepseek-chat",
    latency_ms=350
)

print("✅ 3 logs de test générés dans ~/logs/")
