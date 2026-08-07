\# Agent Analyst – AI Growth Automation System



\## 📌 Présentation



L'Agent Analyst est le 7ᵉ agent du système de marketing automatisé. Il analyse les performances passées, calcule des indicateurs clés (KPIs), génère des rapports et des recommandations, et assure l'observabilité via Langfuse.



\## 🏁 Phases réalisées



\### Phase A – Infrastructure de logs (✅ terminée)

\- Logging structuré (9 champs obligatoires)

\- Audit automatique des logs

\- Ingestion vers PostgreSQL

\- Validation locale et sur VPS



\### Phase B – Intelligence et reporting (✅ terminée)

\- Calcul des 9 KPIs (CPL, CPQ, CPQL, CPBD, ROAS, taux de conversion, temps 1er contact, taux réponse, taux présence)

\- Bot Telegram avec commandes :

&#x20; - `/start` – Bienvenue

&#x20; - `/help` – Liste des commandes

&#x20; - `/health` – État du système (PostgreSQL, Langfuse, LLM)

&#x20; - `/report` – KPIs hebdomadaires

&#x20; - `/weekly\_report` – Rapport d'optimisation

&#x20; - `/alerts` – Détection d'anomalies

&#x20; - `/observe` – Lien vers Langfuse

\- Attribution par source (campagne, ad set, asset)

\- Détection d'anomalies (chute de conversion > 50%)

\- Génération de recommandations via LLM (OpenRouter / DeepSeek)

\- Observabilité complète avec Langfuse



\## 🛠️ Installation



```bash

\# 1. Cloner le dépôt

git clone https://github.com/abderrahmanamaoulouden533-ops/agent-analyst-phaseA.git

cd agent-analyst-phaseA



\# 2. Créer l'environnement virtuel

uv venv

.\\.venv\\Scripts\\Activate.ps1  # Windows

\# source .venv/bin/activate   # Linux/Mac



\# 3. Installer les dépendances

uv pip install -e .



\# 4. Configurer .env (copier .env.example et remplir)

notepad .env



\# 5. Lancer le bot Telegram

cd analyst

python telegram\_report.py

