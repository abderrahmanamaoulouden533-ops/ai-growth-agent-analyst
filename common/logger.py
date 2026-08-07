import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path.home() / "logs"
LOG_DIR.mkdir(exist_ok=True)

def log_action(
    agent_name: str,
    action_type: str,
    input_summary: str,
    output_summary: str,
    client_id: str,
    model_used: str = "rule-based",
    lead_id: str = None,
    latency_ms: int = 0,
):
    """
    Fonction unique de logging pour tous les agents.
    Respecte le format obligatoire du cahier des charges.
    """
    log_entry = {
        "agent_name": agent_name,
        "action_type": action_type,
        "input_summary": input_summary,
        "output_summary": output_summary,
        "lead_id": lead_id,
        "client_id": client_id,
        "model_used": model_used,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Écriture dans le fichier JSON local (backup obligatoire)
    log_file = LOG_DIR / f"{agent_name}_log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry
