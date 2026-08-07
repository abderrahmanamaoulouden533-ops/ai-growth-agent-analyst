"""
common/tracing.py – Wrapper no-op pour Langfuse.
"""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from langfuse import Langfuse
    langfuse = Langfuse()
    print("✅ Langfuse initialisé")
except Exception as e:
    langfuse = None
    print(f"⚠️ Langfuse désactivé : {e}")

def get_tracer():
    return langfuse

def get_langfuse_client():
    """Retourne l'instance Langfuse (peut être None)."""
    return langfuse