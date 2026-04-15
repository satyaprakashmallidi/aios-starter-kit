"""
DataOS — Bitrix24 Collector

Collects CRM contacts, deals, tasks, and calendar events from Bitrix24.
Pulls data via inbound webhook (no extra auth needed).

Requires:
    BITRIX_WEBHOOK_URL — Your Bitrix24 inbound webhook URL

Tables created:
    bitrix_contacts
    bitrix_deals
    bitrix_tasks
    bitrix_events
"""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

try:
    import requests
except ImportError:
    raise ImportError("Missing 'requests' — run: pip install requests")

WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL", "").strip()


def call_bitrix(method, params=None):
    """Call a Bitrix24 REST API method via webhook."""
    if not WEBHOOK_URL:
        return None, "Missing BITRIX_WEBHOOK_URL"

    url = WEBHOOK_URL + method + ".json"
    try:
        payload = params or {}
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            return None, data["error"].get("error_description", str(data["error"]))
        return data.get("result"), None
    except Exception as e:
        return None, str(e)


def collect():
    """Collect all Bitrix24 data."""
    if not WEBHOOK_URL:
        return {
            "source": "bitrix",
            "status": "skipped",
            "reason": "Missing BITRIX_WEBHOOK_URL — add it to .env"
        }

    result = {
        "source": "bitrix",
        "status": "success",
        "data": {}
    }

    # CRM Contacts
    contacts_result, err = call_bitrix("crm.contact.list", {
        "order": {"DATE_CREATE": "DESC"},
        "filter": {},
        "select": ["ID", "NAME", "LAST_NAME", "EMAIL", "PHONE", "COMPANY_TITLE", "DATE_CREATE", "SOURCE_ID"]
    })
    if err:
        result["data"]["contacts"] = []
        result["data"]["_contact_err"] = err
    else:
        result["data"]["contacts"] = contacts_result if contacts_result else []

    # CRM Deals
    deals_result, err = call_bitrix("crm.deal.list", {
        "order": {"DATE_CREATE": "DESC"},
        "filter": {},
        "select": ["ID", "TITLE", "STAGE_ID", "TYPE_ID", "OPPORTUNITY", "CURRENCY_ID", "DATE_CREATE", "CLOSEDATE", "ASSIGNED_BY_ID", "PROBABILITY"]
    })
    if err:
        result["data"]["deals"] = []
        result["data"]["_deal_err"] = err
    else:
        result["data"]["deals"] = deals_result if deals_result else []

    # Tasks (using tasks.task.list method)
    tasks_result, err = call_bitrix("tasks.task.list", {
        "order": {"ID": "DESC"},
        "filter": {}
    })
    if err:
        result["data"]["tasks"] = []
        result["data"]["_task_err"] = err
    else:
        # tasks.task.list returns {"tasks": [...]} not just [...]
        tasks_data = tasks_result if isinstance(tasks_result, dict) else {}
        result["data"]["tasks"] = tasks_data.get("tasks", [])

    total = (len(result["data"]["contacts"]) + len(result["data"]["deals"]) +
              len(result["data"]["tasks"]))
    print(f"  Bitrix: {len(result['data']['contacts'])} contacts, "
          f"{len(result['data']['deals'])} deals, "
          f"{len(result['data']['tasks'])} tasks")

    if result["data"].get("_contact_err") or result["data"].get("_deal_err") or result["data"].get("_task_err"):
        print(f"  Note: {result['data'].get('_contact_err', '')} {result['data'].get('_deal_err', '')} {result['data'].get('_task_err', '')}")

    return result


def write(conn, result, date):
    """Write Bitrix data to database. Returns records written."""
    if result.get("status") != "success":
        conn.commit()
        return 0

    data = result["data"]
    collected_at = datetime.now(timezone.utc).isoformat()

    # Contacts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bitrix_contacts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            company TEXT,
            date_create TEXT,
            source TEXT,
            collected_at TEXT
        )
    """)

    # Deals table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bitrix_deals (
            id INTEGER PRIMARY KEY,
            title TEXT,
            stage_id TEXT,
            deal_type TEXT,
            opportunity REAL,
            currency TEXT,
            date_create TEXT,
            close_date TEXT,
            assigned_to INTEGER,
            probability INTEGER,
            collected_at TEXT
        )
    """)

    # Tasks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bitrix_tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            status TEXT,
            group_name TEXT,
            created_date TEXT,
            deadline TEXT,
            responsible_id INTEGER,
            created_by INTEGER,
            collected_at TEXT
        )
    """)

    records = 0

    # Write contacts
    for c in data.get("contacts", []):
        emails = [e.get("VALUE","") for e in c.get("EMAIL", []) if e]
        phones = [p.get("VALUE","") for p in c.get("PHONE", []) if p]
        conn.execute("""
            INSERT OR REPLACE INTO bitrix_contacts
            (id, name, last_name, email, phone, company, date_create, source, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(c.get("ID", 0)),
            c.get("NAME", ""),
            c.get("LAST_NAME", ""),
            ",".join(emails),
            ",".join(phones),
            c.get("COMPANY_TITLE", ""),
            c.get("DATE_CREATE", ""),
            c.get("SOURCE_ID", ""),
            collected_at
        ))
        records += 1

    # Write deals
    for d in data.get("deals", []):
        conn.execute("""
            INSERT OR REPLACE INTO bitrix_deals
            (id, title, stage_id, deal_type, opportunity, currency, date_create, close_date, assigned_to, probability, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(d.get("ID", 0)),
            d.get("TITLE", ""),
            d.get("STAGE_ID", ""),
            d.get("TYPE_ID", ""),
            float(d.get("OPPORTUNITY", 0) or 0),
            d.get("CURRENCY_ID", ""),
            d.get("DATE_CREATE", ""),
            d.get("CLOSEDATE", ""),
            int(d.get("ASSIGNED_BY_ID", 0) or 0),
            int(d.get("PROBABILITY", 0) or 0),
            collected_at
        ))
        records += 1

    # Write tasks
    for t in data.get("tasks", []):
        group_info = t.get("group", {}) or {}
        conn.execute("""
            INSERT OR REPLACE INTO bitrix_tasks
            (id, title, status, group_name, created_date, deadline, responsible_id, created_by, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(t.get("id", 0)),
            t.get("title", ""),
            t.get("status", ""),
            group_info.get("name", ""),
            t.get("createdDate", ""),
            t.get("deadline", ""),
            int(t.get("responsibleId", 0) or 0),
            int(t.get("createdBy", 0) or 0),
            collected_at
        ))
        records += 1

    conn.commit()
    return records


if __name__ == "__main__":
    result = collect()
    if result["status"] == "success":
        print(f"Collected: contacts={len(result['data']['contacts'])}, "
              f"deals={len(result['data']['deals'])}, "
              f"tasks={len(result['data']['tasks'])}")
    else:
        print(f"{result['status']}: {result.get('reason', '')}")
