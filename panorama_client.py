import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = f"https://{os.getenv('PANORAMA_HOST')}/api/v1/reports/api"


def _headers():
    return {"X-API-Token": os.getenv("PANORAMA_API_KEY")}


def get_institutions():
    r = requests.get(f"{BASE_URL}/institutions/", headers=_headers())
    r.raise_for_status()
    return r.json()


def get_report_queries():
    r = requests.get(f"{BASE_URL}/summary/", headers=_headers())
    r.raise_for_status()
    data = r.json()
    return data["results"] if isinstance(data, dict) else data


def get_report_results(uid, institution, student_group=None, period_days=None, start_date=None, end_date=None):
    params = {"institution": institution}
    if student_group:
        params["student_group"] = student_group
    if period_days:
        params["period_days"] = period_days
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    r = requests.get(f"{BASE_URL}/summary/{uid}/results/", headers=_headers(), params=params)
    r.raise_for_status()
    return r.json()


def get_student_queries():
    r = requests.get(f"{BASE_URL}/student-summary/", headers=_headers())
    r.raise_for_status()
    data = r.json()
    return data["results"] if isinstance(data, dict) else data


def get_student_results(uid, institution, student_group=None, period_days=None, start_date=None, end_date=None):
    params = {"institution": institution}
    if student_group:
        params["student_group"] = student_group
    if period_days:
        params["period_days"] = period_days
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    r = requests.get(f"{BASE_URL}/student-summary/{uid}/results/", headers=_headers(), params=params)
    r.raise_for_status()
    return r.json()
