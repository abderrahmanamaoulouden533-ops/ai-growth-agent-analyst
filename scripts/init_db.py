#!/usr/bin/env python
"""
scripts/init_db.py
Initialise la base de données en exécutant toutes les migrations.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def run_migration(sql_file):
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Migration {sql_file} exécutée.")

if __name__ == "__main__":
    migration_file = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'agent_logs.sql')
    run_migration(migration_file)
    print("🎉 Base de données initialisée.")