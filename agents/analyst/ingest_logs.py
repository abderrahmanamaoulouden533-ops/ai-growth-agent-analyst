import os
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def ingest_logs():
    log_dir = Path.home() / "logs"
    log_files = list(log_dir.glob("*.jsonl"))
    
    if not log_files:
        print(f"⚠️ Aucun fichier trouvé dans {log_dir}")
        return
    
    records = []
    for filepath in log_files:
        print(f"📄 Lecture de {filepath.name}...")
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    records.append((
                        data.get("agent_name"),
                        data.get("action_type"),
                        data.get("input_summary"),
                        data.get("output_summary"),
                        data.get("lead_id"),
                        data.get("client_id"),
                        data.get("model_used"),
                        data.get("latency_ms"),
                        data.get("timestamp")
                    ))
                except json.JSONDecodeError:
                    print(f"⚠️ Ligne ignorée (JSON invalide)")
    
    if not records:
        print("ℹ️ Aucun log valide à ingérer.")
        return
    
    print(f"📊 {len(records)} logs trouvés, insertion dans la base...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        insert_sql = """
            INSERT INTO agent_logs 
            (agent_name, action_type, input_summary, output_summary, lead_id, client_id, model_used, latency_ms, timestamp)
            VALUES %s
        """
        
        execute_values(cur, insert_sql, records, page_size=100)
        conn.commit()
        print(f"✅ {len(records)} logs ingérés avec succès dans la base !")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur d'insertion : {e}")

if __name__ == "__main__":
    ingest_logs()
