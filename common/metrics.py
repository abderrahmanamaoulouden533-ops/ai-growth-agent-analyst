"""
common/metrics.py
Module central de calcul des KPIs – fonctions pures uniquement.
"""

from typing import Dict, Any
from datetime import datetime
import math


def z_test_p_value(success1: int, total1: int, success2: int, total2: int) -> float:
    """
    Retourne la p-value d'un test Z pour deux proportions.
    Utilisé pour déterminer si un A/B test est significatif.
    """
    if total1 == 0 or total2 == 0:
        return 1.0
    p1 = success1 / total1
    p2 = success2 / total2
    p_pooled = (success1 + success2) / (total1 + total2)
    if p_pooled == 0 or p_pooled == 1:
        return 1.0
    se = math.sqrt(p_pooled * (1 - p_pooled) * (1/total1 + 1/total2))
    if se == 0:
        return 1.0
    z = (p1 - p2) / se
    # Approximation normale bilatérale (sans scipy)
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def cpl(total_ad_spend: float, total_form_submissions: int) -> Dict[str, Any]:
    if total_form_submissions == 0:
        return {"value": None, "numerator": total_ad_spend, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_ad_spend / total_form_submissions,
        "numerator": total_ad_spend,
        "denominator": total_form_submissions,
        "data_as_of": datetime.utcnow().isoformat()
    }


def cpq(total_ad_spend: float, leads_with_score_ge_31: int) -> Dict[str, Any]:
    if leads_with_score_ge_31 == 0:
        return {"value": None, "numerator": total_ad_spend, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_ad_spend / leads_with_score_ge_31,
        "numerator": total_ad_spend,
        "denominator": leads_with_score_ge_31,
        "data_as_of": datetime.utcnow().isoformat()
    }


def cpql(total_ad_spend: float, leads_with_score_ge_61: int) -> Dict[str, Any]:
    if leads_with_score_ge_61 == 0:
        return {"value": None, "numerator": total_ad_spend, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_ad_spend / leads_with_score_ge_61,
        "numerator": total_ad_spend,
        "denominator": leads_with_score_ge_61,
        "data_as_of": datetime.utcnow().isoformat()
    }


def cpbd(total_ad_spend: float, appointments_booked: int) -> Dict[str, Any]:
    if appointments_booked == 0:
        return {"value": None, "numerator": total_ad_spend, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_ad_spend / appointments_booked,
        "numerator": total_ad_spend,
        "denominator": appointments_booked,
        "data_as_of": datetime.utcnow().isoformat()
    }


def roas(total_contract_value_closed_won: float, total_ad_spend: float) -> Dict[str, Any]:
    if total_ad_spend == 0:
        return {"value": None, "numerator": total_contract_value_closed_won, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_contract_value_closed_won / total_ad_spend,
        "numerator": total_contract_value_closed_won,
        "denominator": total_ad_spend,
        "data_as_of": datetime.utcnow().isoformat()
    }


def stage_conversion_rate(leads_in_previous_stage: int, leads_in_current_stage: int) -> Dict[str, Any]:
    if leads_in_previous_stage == 0:
        return {"value": None, "numerator": leads_in_current_stage, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": (leads_in_current_stage / leads_in_previous_stage) * 100,
        "numerator": leads_in_current_stage,
        "denominator": leads_in_previous_stage,
        "data_as_of": datetime.utcnow().isoformat()
    }


def time_to_first_contact(total_minutes: float, number_of_contacts: int) -> Dict[str, Any]:
    if number_of_contacts == 0:
        return {"value": None, "numerator": total_minutes, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": total_minutes / number_of_contacts,
        "numerator": total_minutes,
        "denominator": number_of_contacts,
        "data_as_of": datetime.utcnow().isoformat()
    }


def response_rate(replied_first_contacts: int, total_first_contacts: int) -> Dict[str, Any]:
    if total_first_contacts == 0:
        return {"value": None, "numerator": replied_first_contacts, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": (replied_first_contacts / total_first_contacts) * 100,
        "numerator": replied_first_contacts,
        "denominator": total_first_contacts,
        "data_as_of": datetime.utcnow().isoformat()
    }


def meeting_show_rate(leads_showed_up: int, total_meetings_booked: int) -> Dict[str, Any]:
    if total_meetings_booked == 0:
        return {"value": None, "numerator": leads_showed_up, "denominator": 0, "data_as_of": datetime.utcnow().isoformat()}
    return {
        "value": (leads_showed_up / total_meetings_booked) * 100,
        "numerator": leads_showed_up,
        "denominator": total_meetings_booked,
        "data_as_of": datetime.utcnow().isoformat()
    }


def get_all_metrics(data: dict) -> dict:
    return {
        "cpl": cpl(data["ad_spend"], data["submissions"]),
        "cpq": cpq(data["ad_spend"], data["leads_ge_31"]),
        "cpql": cpql(data["ad_spend"], data["leads_ge_61"]),
        "cpbd": cpbd(data["ad_spend"], data["appointments"]),
        "roas": roas(data["closed_won_value"], data["ad_spend"]),
        "stage_conversion": stage_conversion_rate(data["prev_stage_leads"], data["curr_stage_leads"]),
        "time_to_first_contact": time_to_first_contact(data["total_minutes_contact"], data["contacts_count"]),
        "response_rate": response_rate(data["replied_first_contacts"], data["total_first_contacts"]),
        "meeting_show_rate": meeting_show_rate(data["showed_up"], data["total_meetings"])
    }