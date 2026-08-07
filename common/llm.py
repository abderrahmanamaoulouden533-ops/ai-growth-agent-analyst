"""
common/llm.py – Appels LLM via OpenRouter (avec fallback).
"""
import os
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    try:
        from litellm import completion
        return completion
    except ImportError:
        return None

def generate_llm_response(prompt: str, system_prompt: str = "Tu es un analyste marketing.") -> str:
    llm = get_llm()
    if not llm:
        return "⚠️ LLM non disponible"
    try:
        resp = llm(
            model=os.getenv("MODEL_NAME", "openrouter/deepseek/deepseek-chat"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Erreur LLM: {e}")
        return "Erreur de génération"