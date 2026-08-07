import json
import glob
from pydantic import BaseModel, ValidationError

class LogEntry(BaseModel):
    agent_name: str
    action_type: str
    input_summary: str
    output_summary: str
    lead_id: str | None
    client_id: str
    model_used: str
    latency_ms: int
    timestamp: str

def audit_all_logs():
    log_files = glob.glob("../commander/logs/*.jsonl") + \
                glob.glob("../crm_keeper/logs/*.jsonl") + \
                glob.glob("../qualifier/logs/*.jsonl")
    
    errors = []
    for filepath in log_files:
        try:
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line: continue
                    try:
                        data = json.loads(line)
                        LogEntry(**data)
                    except (json.JSONDecodeError, ValidationError) as e:
                        errors.append(f"❌ {filepath} ligne {line_num} : {e}")
        except FileNotFoundError:
            errors.append(f"⚠️ Fichier manquant : {filepath}")
    
    if errors:
        print("🔴 AUDIT ÉCHOUÉ :")
        for err in errors:
            print(err)
    else:
        print("✅ AUDIT RÉUSSI : Tous les logs sont parfaitement conformes au contrat !")

if __name__ == "__main__":
    audit_all_logs()
