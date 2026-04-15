"""
IntelOS — Bitrix meeting collector.

Pulls calendar events and CRM activities from Bitrix24 as meeting-like records.
Uses the existing BITRIX_WEBHOOK_URL from .env (no extra API key needed).

Collection strategy:
1. Try CRM activity log (calls & meetings) — works with webhook auth
2. If calendar methods are available, pull calendar events too

Note: Full calendar API requires user OAuth, not webhook. The CRM activity log
is the most reliable option for capturing meeting/call history via webhook.

Usage:
    python scripts/intel/collect_bitrix_meetings.py          # Last 7 days
    python scripts/intel/collect_bitrix_meetings.py --days 30
"""

import os
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL", "").strip()

# Activity type IDs in Bitrix CRM
# 2 = meeting, 4 = call, 3 = email, 1 = to-do
MEETING_TYPES = [2, 4]


def call_bitrix(method: str, params: dict = None) -> tuple:
    """Call a Bitrix24 REST API method via webhook. Returns (result, error)."""
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
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP {e.response.status_code}"
    except Exception as e:
        return None, str(e)


def _parse_datetime(dt_str: str, fallback_date: str) -> tuple:
    """Parse a date/time string. Returns (date_str, time_str)."""
    if not dt_str:
        return fallback_date, None
    try:
        # Try ISO format with timezone
        if "T" in dt_str:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        else:
            dt = datetime.strptime(dt_str[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return dt_str[:10] if dt_str else fallback_date, None


def collect_activities(days: int = 7) -> list[dict]:
    """Collect CRM activities (calls & meetings) from Bitrix24."""
    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    result, err = call_bitrix("crm.activity.list", {
        "filter": {
            ">CREATED": start_date,
            "<CREATED": end_date,
            "TYPE_ID": MEETING_TYPES,
        },
        "select": ["ID", "SUBJECT", "DESCRIPTION", "CREATED", "END_TIME",
                   "RESPONSIBLE_ID", "PHONE", "ASSOCIATED_ENTITY_ID"]
    })

    if err:
        return []

    activities = result if isinstance(result, list) else result.get("result", []) if isinstance(result, dict) else []
    meetings = []

    for act in activities:
        act_id = str(act.get("ID", ""))
        if not act_id:
            continue

        date_str, start_time = _parse_datetime(act.get("CREATED", ""), start_date)
        end_time_str = act.get("END_TIME", "")

        duration_minutes = None
        if act.get("CREATED") and end_time_str:
            try:
                fmt = "%Y-%m-%d %H:%M:%S"
                dt_start = datetime.strptime(act["CREATED"][:19], fmt)
                dt_end = datetime.strptime(end_time_str[:19], fmt)
                duration_minutes = int((dt_end - dt_start).total_seconds() / 60)
            except (ValueError, TypeError):
                pass

        activity_type = act.get("TYPE_ID", 2)
        type_label = "Call" if activity_type == 4 else "Meeting"

        meetings.append({
            "meeting_id": f"bitrix_{act_id}",
            "source": "bitrix",
            "title": act.get("SUBJECT", "") or f"{type_label}",
            "date": date_str,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "participants": "[]",
            "transcript_text": act.get("DESCRIPTION", "") or "",
            "summary": f"Bitrix {type_label} — {date_str}",
            "action_items_raw": None,
            "external_url": None,
        })

    return meetings


def collect_calendar_events(days: int = 7) -> list[dict]:
    """Try to collect calendar events. May fail if calendar access isn't enabled."""
    result, err = call_bitrix("calendar.event.get", {"type": "user", "userId": 0})
    if err:
        return []  # Calendar not accessible via webhook — that's fine

    events = result.get("events", []) if isinstance(result, dict) else (result if isinstance(result, list) else [])

    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")

    meetings = []
    for event in events:
        event_id = str(event.get("ID", ""))
        if not event_id:
            continue

        date_from = event.get("DATE_FROM", "")
        date_to = event.get("DATE_TO", "")

        date_str, start_time = _parse_datetime(date_from, start_date)

        duration_minutes = None
        if date_from and date_to:
            try:
                fmt = "%Y-%m-%dT%H:%M:%S%z" if "T" in date_from else "%Y-%m-%d %H:%M:%S"
                dt_start = datetime.fromisoformat(date_from.replace("Z", "+00:00")) if "T" in date_from else datetime.strptime(date_from[:19], "%Y-%m-%d %H:%M:%S")
                dt_end = datetime.fromisoformat(date_to.replace("Z", "+00:00")) if "T" in date_to else datetime.strptime(date_to[:19], "%Y-%m-%d %H:%M:%S")
                duration_minutes = int((dt_end - dt_start).total_seconds() / 60)
            except (ValueError, TypeError):
                pass

        attendees = []
        for att in (event.get("ATTENDEE_LIST", []) or []):
            if isinstance(att, dict):
                attendees.append({
                    "name": att.get("NAME", ""),
                    "email": att.get("EMAIL", ""),
                })

        meetings.append({
            "meeting_id": f"bitrix_cal_{event_id}",
            "source": "bitrix",
            "title": event.get("NAME", "") or event.get("TITLE", "") or "Calendar Event",
            "date": date_str,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "participants": json.dumps(attendees) if attendees else "[]",
            "transcript_text": event.get("DESCRIPTION", "") or "",
            "summary": f"Bitrix Calendar Event — {len(attendees)} attendee(s)",
            "action_items_raw": None,
            "external_url": None,
        })

    return meetings


def collect(days: int = 7) -> list[dict]:
    """
    Collect meeting data from Bitrix24 (activities + calendar events).
    Returns a list of meeting dicts ready for db.write_meetings().
    """
    if not WEBHOOK_URL:
        print("Skipped: BITRIX_WEBHOOK_URL not set in .env")
        return []

    meetings = []

    # Primary: CRM activities (calls & meetings) — always works with webhook
    activities = collect_activities(days)
    if activities:
        meetings.extend(activities)
        print(f"Bitrix: collected {len(activities)} CRM activities (calls/meetings)")
    else:
        print("Bitrix: no CRM activities found in the last 7 days")

    # Secondary: calendar events — try, but don't fail if unavailable
    try:
        cal_events = collect_calendar_events(days)
        if cal_events:
            meetings.extend(cal_events)
            print(f"Bitrix: collected {len(cal_events)} calendar events")
    except Exception:
        pass  # Calendar access is optional

    return meetings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect Bitrix CRM activities as meetings")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    args = parser.parse_args()

    meetings = collect(days=args.days)
    if meetings:
        print(f"\nSample: {meetings[0]['title']} ({meetings[0]['date']})")
    else:
        print("\nNo meetings collected — no CRM activities in the last 7 days,")
        print("or calendar access is not enabled on this Bitrix plan.")
