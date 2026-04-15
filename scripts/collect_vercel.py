"""
DataOS — Vercel Collector

Collects deployments and projects from Vercel.
Pulls data via the Vercel REST API using an API token.

Requires:
    VERCEL_TOKEN — Vercel API Token

Tables created:
    vercel_deployments
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

TOKEN = os.getenv("VERCEL_TOKEN", "").strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def vc_get(url, params=None):
    """Make a Vercel API request."""
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)


def collect():
    """Collect all Vercel data."""
    if not TOKEN:
        return {"source": "vercel", "status": "skipped", "reason": "Missing VERCEL_TOKEN"}

    result = {"source": "vercel", "status": "success", "data": {}}

    # User info
    user, err = vc_get("https://api.vercel.com/v2/user")
    if err:
        result["data"]["user"] = {}
        result["data"]["_user_err"] = err
    else:
        u = user.get("user", {})
        result["data"]["user"] = {
            "username": u.get("username", ""),
            "email": u.get("email", ""),
            "name": u.get("name", ""),
        }

    # Deployments (recent 20)
    deps, err = vc_get("https://api.vercel.com/v6/deployments", {"limit": 20})
    if err:
        result["data"]["deployments"] = []
        result["data"]["_deps_err"] = err
    else:
        deployments = deps.get("deployments", [])
        result["data"]["deployments"] = [{
            "uid": d.get("uid", ""),
            "name": d.get("name", ""),
            "url": d.get("url", ""),
            "state": d.get("state", ""),
            "ready_state": d.get("readyState", ""),
            "source": d.get("source", ""),
            "created_at": datetime.fromtimestamp(d.get("createdAt", 0)/1000).isoformat() if d.get("createdAt") else "",
            "ready_at": datetime.fromtimestamp(d.get("ready", 0)/1000).isoformat() if d.get("ready") else "",
            "github_org": d.get("meta", {}).get("githubOrg", ""),
            "github_repo": d.get("meta", {}).get("githubRepo", ""),
            "github_commit_message": d.get("meta", {}).get("githubCommitMessage", ""),
            "github_branch": d.get("meta", {}).get("githubCommitRef", ""),
            "error": d.get("errorMessage", ""),
        } for d in deployments]

    # Projects
    projects, _ = vc_get("https://api.vercel.com/v2/projects")
    if isinstance(projects, dict):
        proj_list = projects.get("projects", [])
    elif isinstance(projects, list):
        proj_list = projects
    else:
        proj_list = []
    result["data"]["projects"] = [{
        "uid": p.get("id", ""),
        "name": p.get("name", ""),
        "framework": p.get("framework", ""),
        "git_repository": p.get("link", {}).get("repo", ""),
    } for p in proj_list]

    print(f"  Vercel: {len(result['data']['deployments'])} deployments, "
          f"{len(result['data']['projects'])} projects")
    return result


def write(conn, result, date):
    """Write Vercel data to database. Returns records written."""
    if result.get("status") != "success":
        conn.commit()
        return 0

    data = result["data"]
    collected_at = datetime.now(timezone.utc).isoformat()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS vercel_deployments (
            uid TEXT PRIMARY KEY,
            name TEXT,
            url TEXT,
            state TEXT,
            ready_state TEXT,
            source TEXT,
            created_at TEXT,
            ready_at TEXT,
            github_org TEXT,
            github_repo TEXT,
            github_commit_message TEXT,
            github_branch TEXT,
            error TEXT,
            collected_at TEXT
        )
    """)

    records = 0
    for d in data.get("deployments", []):
        conn.execute("""
            INSERT OR REPLACE INTO vercel_deployments
            (uid, name, url, state, ready_state, source, created_at, ready_at,
             github_org, github_repo, github_commit_message, github_branch, error, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d["uid"], d["name"], d["url"], d["state"], d["ready_state"], d["source"],
            d["created_at"], d["ready_at"], d["github_org"], d["github_repo"],
            d["github_commit_message"], d["github_branch"], d["error"], collected_at
        ))
        records += 1

    conn.commit()
    return records


if __name__ == "__main__":
    result = collect()
    if result["status"] == "success":
        print(f"Deployments: {len(result['data']['deployments'])}, "
              f"Projects: {len(result['data']['projects'])}")
    else:
        print(f"{result['status']}: {result.get('reason', '')}")
