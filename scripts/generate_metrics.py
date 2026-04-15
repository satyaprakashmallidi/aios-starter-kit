"""
DataOS — Key Metrics Generator

Reads the database and generates a human-readable key-metrics.md file.
This file is loaded by your /prime command so your AI always has fresh data.

Automatically discovers which tables exist and generates sections for each.

Usage:
    python scripts/generate_metrics.py
"""

import sqlite3
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE_ROOT / "data" / "data.db"
OUTPUT_PATH = WORKSPACE_ROOT / "context" / "group" / "key-metrics.md"


def fmt_number(value, prefix="", suffix=""):
    """Format a number with commas. Returns 'No data' if None."""
    if value is None:
        return "No data"
    if isinstance(value, float):
        return f"{prefix}{value:,.0f}{suffix}"
    return f"{prefix}{value:,}{suffix}"


def fmt_currency(value, symbol="$"):
    """Format currency value with symbol and commas."""
    if value is None:
        return "No data"
    return f"{symbol}{value:,.0f}"


def fmt_pct(value):
    """Format a percentage to 1 decimal place."""
    if value is None:
        return "No data"
    return f"{value:.1f}%"


def query_one(conn, sql):
    """Query helper — returns first row as dict or None."""
    try:
        row = conn.execute(sql).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def query_all(conn, sql):
    """Query helper — returns all rows as list of dicts."""
    try:
        return [dict(r) for r in conn.execute(sql).fetchall()]
    except Exception:
        return []


def table_exists(conn, name):
    """Check if a table exists."""
    r = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return r is not None


def section_fx_rates(conn):
    """FX rates — the starter collector (always available)."""
    if not table_exists(conn, "fx_rates"):
        return []
    lines = []
    lines.append("## Exchange Rates")
    lines.append("| Currency | Rate (from USD) | As Of |")
    lines.append("|----------|----------------|-------|")
    rows = query_all(conn, """
        SELECT date, currency, rate FROM fx_rates
        WHERE date = (SELECT MAX(date) FROM fx_rates)
        ORDER BY currency
    """)
    for r in rows:
        lines.append(f"| {r['currency']} | {r['rate']:.4f} | {r['date']} |")
    lines.append("")
    return lines


def section_bitrix_tasks(conn):
    """Bitrix24 tasks."""
    if not table_exists(conn, "bitrix_tasks"):
        return []
    lines = ["## Bitrix24 Tasks"]
    rows = query_all(conn, "SELECT COUNT(*) as total, COUNT(CASE WHEN status='2' THEN 1 END) as completed FROM bitrix_tasks")
    if rows:
        r = rows[0]
        lines.append(f"| Total Tasks | {r['total']} |")
        lines.append(f"| Completed | {r['completed']} |")
    rows = query_all(conn, "SELECT title, status, group_name, deadline FROM bitrix_tasks ORDER BY id DESC LIMIT 5")
    if rows:
        lines.append("| Recent Tasks | Status | Project | Deadline |")
        lines.append("|-------------|--------|---------|----------|")
        for r in rows:
            status = "Done" if r["status"] == "2" else "In Progress"
            lines.append(f"| {r['title']} | {status} | {r['group_name'] or '-'} | {r['deadline'] or '-'} |")
    lines.append("")
    return lines


def section_github(conn):
    """GitHub repositories and activity."""
    if not table_exists(conn, "github_repos"):
        return []
    lines = ["## GitHub"]
    row = query_one(conn, "SELECT COUNT(*) as total, SUM(stargazers_count) as stars, SUM(open_issues_count) as issues FROM github_repos")
    if row:
        lines.append(f"| Repositories | {row['total']} |")
        lines.append(f"| Stars | {row['stars'] or 0} |")
        lines.append(f"| Open Issues | {row['issues'] or 0} |")
    rows = query_all(conn, "SELECT full_name, language, pushed_at FROM github_repos ORDER BY pushed_at DESC LIMIT 5")
    if rows:
        lines.append("| Recent Repos | Language | Last Push |")
        lines.append("|-------------|----------|-----------|")
        for r in rows:
            lines.append(f"| {r['full_name']} | {r['language'] or '-'} | {r['pushed_at'][:10] if r['pushed_at'] else '-'} |")
    lines.append("")
    return lines


def section_vercel(conn):
    """Vercel deployments."""
    if not table_exists(conn, "vercel_deployments"):
        return []
    lines = ["## Vercel"]
    rows = query_all(conn, """
        SELECT state, COUNT(*) as cnt FROM vercel_deployments
        GROUP BY state
    """)
    if rows:
        lines.append("| Deployment State | Count |")
        lines.append("|-----------------|-------|")
        for r in rows:
            lines.append(f"| {r['state']} | {r['cnt']} |")
    rows = query_all(conn, """
        SELECT name, state, github_repo, github_commit_message, ready_at
        FROM vercel_deployments ORDER BY ready_at DESC LIMIT 5
    """)
    if rows:
        lines.append("| Recent Deployments | State | GitHub Repo | Commit |")
        lines.append("|-------------------|-------|-------------|--------|")
        for r in rows:
            commit = (r['github_commit_message'] or '')[:40]
            lines.append(f"| {r['name']} | {r['state']} | {r['github_repo'] or '-'} | {commit} |")
    lines.append("")
    return lines


# --- CUSTOMIZATION ZONE ---
# Claude adds your custom section functions below during installation.
# Each follows the same pattern:
#
#   def section_NAME(conn):
#       if not table_exists(conn, "TABLE_NAME"):
#           return []
#       lines = ["## Section Title", "| Metric | Value | As Of |", ...]
#       row = query_one(conn, "SELECT ... FROM TABLE_NAME ORDER BY date DESC LIMIT 1")
#       if row:
#           lines.append(f"| Metric | {fmt_number(row['value'])} | {row['date']} |")
#       return lines


# ============================================================
# MAIN GENERATOR
# ============================================================

SECTIONS = [
    section_fx_rates,
    section_bitrix_tasks,
    section_github,
    section_vercel,
]


def generate(conn):
    """Generate the key-metrics markdown content."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "# Key Metrics",
        "",
        f"> Auto-generated from database. Last updated: {today}",
        f"> Source: `data/data.db` | Regenerate: `python scripts/generate_metrics.py`",
        "",
    ]

    for section_fn in SECTIONS:
        try:
            section_lines = section_fn(conn)
            if section_lines:
                lines.extend(section_lines)
        except Exception as e:
            lines.append(f"<!-- Error in {section_fn.__name__}: {e} -->")
            lines.append("")

    # Data freshness table
    lines.append("## Data Freshness")
    lines.append("| Source | Latest Record | Status |")
    lines.append("|--------|---------------|--------|")

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name != 'collection_log' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()

    for t in tables:
        name = t["name"]
        try:
            row = conn.execute(f"SELECT MAX(date) as d FROM {name}").fetchone()
            if row and row["d"]:
                lines.append(f"| {name} | {row['d']} | Connected |")
            else:
                lines.append(f"| {name} | — | Empty |")
        except Exception:
            lines.append(f"| {name} | — | No date column |")

    lines.append("")
    return "\n".join(lines)


def main():
    """Generate key-metrics.md from the database."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Run collection first: python scripts/collect.py")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    content = generate(conn)
    conn.close()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content)
    print(f"Key metrics written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
