"""
common/db.py – Connexion centralisée à PostgreSQL.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Retourne une connexion PostgreSQL (gère l'encodage)."""
    return psycopg2.connect(DATABASE_URL)