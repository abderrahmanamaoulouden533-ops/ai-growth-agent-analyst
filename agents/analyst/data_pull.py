"""
data_pull.py
Lecture des données depuis PostgreSQL pour les métriques.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
from common.db import get_db_connection
import psycopg2


def get_ad_spend(client_id: str, start_date: str, end_date: str) -> float:
    """
    Retourne le total des dépenses publicitaires pour un client sur une période.

    Args:
        client_id: Identifiant du client.
        start_date: Date de début (format YYYY-MM-DD).
        end_date: Date de fin (format YYYY-MM-DD).

    Returns:
        float: Total des dépenses.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(spend), 0) 
        FROM ad_spend 
        WHERE client_id = %s AND date BETWEEN %s AND %s
    """, (client_id, start_date, end_date))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return float(result)


def get_total_form_submissions(client_id: str, start_date: str, end_date: str) -> int:
    """
    Compte les leads créés dans la période (tous les leads).

    Args:
        client_id: Identifiant du client.
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        int: Nombre de leads créés.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) 
        FROM leads 
        WHERE client_id = %s AND created_at::date BETWEEN %s::date AND %s::date
    """, (client_id, start_date, end_date))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def get_leads_with_score_ge(client_id: str, min_score: int, start_date: str, end_date: str) -> int:
    """
    Compte les leads avec un score >= min_score sur la période.

    Args:
        client_id: Identifiant du client.
        min_score: Score minimum (31 pour MQL, 61 pour SQL).
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        int: Nombre de leads avec score >= min_score.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) 
        FROM leads 
        WHERE client_id = %s 
        AND qualification_score >= %s
        AND created_at::date BETWEEN %s::date AND %s::date
    """, (client_id, min_score, start_date, end_date))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def get_appointments_booked(client_id: str, start_date: str, end_date: str) -> int:
    """
    Compte les rendez-vous pris sur la période.

    Args:
        client_id: Identifiant du client.
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        int: Nombre de rendez-vous pris.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) 
        FROM bookings b
        JOIN leads l ON b.lead_id = l.lead_id
        WHERE l.client_id = %s 
        AND b.booked_at::date BETWEEN %s::date AND %s::date
    """, (client_id, start_date, end_date))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def get_closed_won_value(client_id: str, start_date: str, end_date: str) -> float:
    """
    Total des valeurs des deals closed_won sur la période.

    Args:
        client_id: Identifiant du client.
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        float: Total des valeurs closed_won.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(contract_value), 0) 
        FROM leads 
        WHERE client_id = %s 
        AND lead_stage = 'closed_won'
        AND created_at::date BETWEEN %s::date AND %s::date
    """, (client_id, start_date, end_date))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return float(result)


def get_stage_counts(client_id: str, stage: str, start_date: str, end_date: str) -> int:
    """
    Compte les leads dans une étape donnée sur une période.

    Args:
        client_id: Identifiant du client.
        stage: Étape du pipeline (new, mql, sql, contacted, meeting_booked, closed_won, closed_lost).
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        int: Nombre de leads dans l'étape.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) 
        FROM leads 
        WHERE client_id = %s 
        AND lead_stage = %s
        AND created_at::date BETWEEN %s::date AND %s::date
    """, (client_id, stage, start_date, end_date))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def get_time_to_first_contact(client_id: str, start_date: str, end_date: str) -> dict:
    """
    Calcule le temps moyen (en minutes) entre la création d'un lead et le premier message du Closer.
    Target: under 5 minutes.

    Args:
        client_id: Identifiant du client.
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        dict: {"total_minutes": float, "count": int}
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            AVG(EXTRACT(EPOCH FROM (cl.timestamp - l.created_at)) / 60) as avg_minutes,
            COUNT(DISTINCT l.lead_id) as contact_count
        FROM agent_logs cl
        JOIN leads l ON cl.lead_id = l.lead_id::text
        WHERE l.client_id = %s
          AND cl.agent_name = 'closer'
          AND cl.action_type = 'send_message'
          AND l.created_at::date BETWEEN %s::date AND %s::date
          AND cl.timestamp > l.created_at
    """, (client_id, start_date, end_date))
    row = cur.fetchone()
    cur.close()
    conn.close()
    avg_minutes = row[0] if row and row[0] is not None else 0.0
    count = row[1] if row and row[1] is not None else 0
    return {"total_minutes": float(avg_minutes), "count": int(count)}


def get_response_rate(client_id: str, start_date: str, end_date: str) -> dict:
    """
    Calcule le taux de réponse aux premiers messages dans les 48h.

    Args:
        client_id: Identifiant du client.
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        dict: {"replied_first_contacts": int, "total_first_contacts": int}
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            COUNT(DISTINCT l.lead_id) as total_first_contacts,
            COUNT(DISTINCT r.lead_id) as replied
        FROM agent_logs l
        LEFT JOIN agent_logs r ON l.lead_id = r.lead_id
            AND r.action_type = 'reply'
            AND r.agent_name = 'analyst'
            AND r.timestamp BETWEEN l.timestamp AND l.timestamp + INTERVAL '48 hours'
        WHERE l.client_id = %s
          AND l.agent_name = 'closer'
          AND l.action_type = 'send_message'
          AND l.timestamp::date BETWEEN %s::date AND %s::date
    """, (client_id, start_date, end_date))
    row = cur.fetchone()
    cur.close()
    conn.close()
    total = row[0] if row and row[0] is not None else 0
    replied = row[1] if row and row[1] is not None else 0
    return {"replied_first_contacts": int(replied), "total_first_contacts": int(total)}


def get_meeting_show_rate(client_id: str, start_date: str, end_date: str) -> dict:
    """
    Calcule le taux de présence aux rendez-vous.

    Args:
        client_id: Identifiant du client.
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        dict: {"total_meetings": int, "showed_up": int}
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            COUNT(*) as total_booked,
            COUNT(CASE WHEN showed_up = true THEN 1 END) as showed_up
        FROM bookings b
        JOIN leads l ON b.lead_id = l.lead_id
        WHERE l.client_id = %s
          AND b.booked_at::date BETWEEN %s::date AND %s::date
    """, (client_id, start_date, end_date))
    row = cur.fetchone()
    cur.close()
    conn.close()
    total = row[0] if row and row[0] is not None else 0
    showed = row[1] if row and row[1] is not None else 0
    return {"total_meetings": int(total), "showed_up": int(showed)}


def get_all_kpi_data(client_id: str, start_date: str, end_date: str) -> dict:
    """
    Récupère toutes les données nécessaires pour les KPIs en une seule fois.

    Args:
        client_id: Identifiant du client.
        start_date: Date de début.
        end_date: Date de fin.

    Returns:
        dict: Dictionnaire contenant toutes les données pour les KPIs.
    """
    ad_spend = get_ad_spend(client_id, start_date, end_date)
    submissions = get_total_form_submissions(client_id, start_date, end_date)
    leads_ge_31 = get_leads_with_score_ge(client_id, 31, start_date, end_date)
    leads_ge_61 = get_leads_with_score_ge(client_id, 61, start_date, end_date)
    appointments = get_appointments_booked(client_id, start_date, end_date)
    closed_value = get_closed_won_value(client_id, start_date, end_date)

    new_leads = get_stage_counts(client_id, 'new', start_date, end_date)
    mql_leads = get_stage_counts(client_id, 'mql', start_date, end_date)

    time_data = get_time_to_first_contact(client_id, start_date, end_date)
    resp_data = get_response_rate(client_id, start_date, end_date)
    show_data = get_meeting_show_rate(client_id, start_date, end_date)

    return {
        "ad_spend": ad_spend,
        "submissions": submissions,
        "leads_ge_31": leads_ge_31,
        "leads_ge_61": leads_ge_61,
        "appointments": appointments,
        "closed_won_value": closed_value,
        "prev_stage_leads": new_leads,
        "curr_stage_leads": mql_leads,
        "total_minutes_contact": time_data["total_minutes"],
        "contacts_count": time_data["count"],
        "replied_first_contacts": resp_data["replied_first_contacts"],
        "total_first_contacts": resp_data["total_first_contacts"],
        "showed_up": show_data["showed_up"],
        "total_meetings": show_data["total_meetings"]
    }