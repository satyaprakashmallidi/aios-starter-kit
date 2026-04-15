"""
DataOS — GitHub Collector

Collects repositories, recent commits, and issues from GitHub.
Pulls data via the GitHub REST API using a Personal Access Token.

Requires:
    GITHUB_TOKEN — GitHub Personal Access Token

Tables created:
    github_repos
    github_commits
    github_issues
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

TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"} if TOKEN else {}


def gh_get(url, params=None):
    """Make a GitHub API request."""
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)


def collect():
    """Collect all GitHub data."""
    if not TOKEN:
        return {"source": "github", "status": "skipped", "reason": "Missing GITHUB_TOKEN"}

    result = {"source": "github", "status": "success", "data": {}}

    # User profile
    user, err = gh_get("https://api.github.com/user")
    if err:
        result["data"]["user"] = {}
        result["data"]["_user_err"] = err
    else:
        result["data"]["user"] = {
            "login": user.get("login", ""),
            "name": user.get("name", ""),
            "public_repos": user.get("public_repos", 0),
            "total_private_repos": user.get("total_private_repos", 0),
            "followers": user.get("followers", 0),
        }

    # Repositories
    repos, err = gh_get("https://api.github.com/user/repos", {"per_page": 30, "sort": "updated"})
    if err:
        result["data"]["repos"] = []
        result["data"]["_repos_err"] = err
    else:
        result["data"]["repos"] = [{
            "name": r.get("name", ""),
            "full_name": r.get("full_name", ""),
            "description": r.get("description", ""),
            "language": r.get("language", ""),
            "stargazers_count": r.get("stargazers_count", 0),
            "forks_count": r.get("forks_count", 0),
            "open_issues_count": r.get("open_issues_count", 0),
            "updated_at": r.get("updated_at", ""),
            "pushed_at": r.get("pushed_at", ""),
            "default_branch": r.get("default_branch", ""),
            "private": r.get("private", False),
        } for r in repos]

    # Recent commits (last 7 days across all repos)
    commits = []
    for r in result["data"].get("repos", [])[:10]:  # top 10 updated repos
        owner, name = r["full_name"].split("/")
        commits_url = f"https://api.github.com/repos/{owner}/{name}/commits"
        c_data, _ = gh_get(commits_url, {"per_page": 5})
        if c_data:
            for c in c_data:
                author = c.get("commit", {}).get("author", {}) or {}
                commits.append({
                    "repo": r["full_name"],
                    "sha": c.get("sha", "")[:8],
                    "message": (c.get("commit", {}).get("message", "") or "").split("\n")[0],
                    "author": author.get("name", ""),
                    "date": author.get("date", ""),
                })
    result["data"]["commits"] = commits

    # Open issues
    issues = []
    for r in result["data"].get("repos", [])[:10]:
        owner, name = r["full_name"].split("/")
        i_data, _ = gh_get(f"https://api.github.com/repos/{owner}/{name}/issues", {"state": "open", "per_page": 5})
        if i_data:
            for i in i_data:
                issues.append({
                    "repo": r["full_name"],
                    "number": i.get("number", 0),
                    "title": i.get("title", ""),
                    "state": i.get("state", ""),
                    "created_at": i.get("created_at", ""),
                    "labels": ",".join([l.get("name","") for l in i.get("labels", [])]),
                })
    result["data"]["issues"] = issues

    print(f"  GitHub: {len(result['data']['repos'])} repos, "
          f"{len(result['data']['commits'])} recent commits, "
          f"{len(result['data']['issues'])} open issues")
    return result


def write(conn, result, date):
    """Write GitHub data to database. Returns records written."""
    if result.get("status") != "success":
        conn.commit()
        return 0

    data = result["data"]
    collected_at = datetime.now(timezone.utc).isoformat()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS github_repos (
            name TEXT PRIMARY KEY,
            full_name TEXT,
            description TEXT,
            language TEXT,
            stargazers_count INTEGER,
            forks_count INTEGER,
            open_issues_count INTEGER,
            updated_at TEXT,
            pushed_at TEXT,
            default_branch TEXT,
            is_private INTEGER,
            collected_at TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS github_commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT,
            sha TEXT,
            message TEXT,
            author TEXT,
            date TEXT,
            collected_at TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS github_issues (
            repo TEXT,
            number INTEGER,
            title TEXT,
            state TEXT,
            created_at TEXT,
            labels TEXT,
            collected_at TEXT,
            PRIMARY KEY (repo, number)
        )
    """)

    records = 0

    for r in data.get("repos", []):
        conn.execute("""
            INSERT OR REPLACE INTO github_repos
            (name, full_name, description, language, stargazers_count, forks_count,
             open_issues_count, updated_at, pushed_at, default_branch, is_private, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["name"], r["full_name"], r["description"], r["language"],
            r["stargazers_count"], r["forks_count"], r["open_issues_count"],
            r["updated_at"], r["pushed_at"], r["default_branch"],
            1 if r["private"] else 0, collected_at
        ))
        records += 1

    for c in data.get("commits", []):
        conn.execute("""
            INSERT INTO github_commits (repo, sha, message, author, date, collected_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (c["repo"], c["sha"], c["message"], c["author"], c["date"], collected_at))
        records += 1

    for i in data.get("issues", []):
        conn.execute("""
            INSERT OR REPLACE INTO github_issues (repo, number, title, state, created_at, labels, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (i["repo"], i["number"], i["title"], i["state"], i["created_at"], i["labels"], collected_at))
        records += 1

    conn.commit()
    return records


if __name__ == "__main__":
    result = collect()
    if result["status"] == "success":
        print(f"Repos: {len(result['data']['repos'])}, "
              f"Commits: {len(result['data']['commits'])}, "
              f"Issues: {len(result['data']['issues'])}")
    else:
        print(f"{result['status']}: {result.get('reason', '')}")
