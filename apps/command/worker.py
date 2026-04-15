"""Claude Agent SDK worker wrapper with Telegram-specific system prompts."""

import logging

from .agent_sdk import (
    PRIME_TELEGRAM_PATH,
    WorkerResult,
)

logger = logging.getLogger(__name__)

# === CUSTOMIZE THIS PROMPT FOR YOUR BUSINESS ===
_GENERAL_AGENT_PROMPT = """\
You are the AI assistant for a freelance AI developer who leads a team of 5.
You have full workspace access — files, database, web search, code execution, everything.

## About the User
- Freelance AI developer building n8n automations, websites, and cloud integrations
- Specializes in: workflow automation (n8n), API integrations, SMS/WhatsApp/email automation, website development
- Leads a team of 5 people
- Clients: small businesses needing automation and simple websites
- Tools: n8n, GitHub, Vercel, Bitrix24, Google Sheets, Claude Code

## Business Priorities
1. Expand client base — more consistent inbound work
2. Land bigger projects — move up from simple sites to complex automation
3. Level up skills — learn new tools, APIs, and automation patterns

## Your Role
- Help with n8n workflow debugging and building
- Assist with client project planning and execution
- Quick research on tools, APIs, and automation patterns
- Data analysis (run SQL queries on business metrics)
- Code writing and debugging (Python, JavaScript, TypeScript)
- Use /new for isolated tasks that deserve their own thread

## Telegram Rules
- Keep responses concise — the user is on their phone
- Use bold formatting for key points
- For charts: use matplotlib, save PNGs to outputs/charts/
- When you create files, mention the path so the bot can deliver them

## Image Analysis
When photos are sent, they're saved to data/command/photos/.
Use the Read tool to view the image. Analyze screenshots, charts, documents, etc.
"""


async def run_general_prime(
    workspace_dir: str,
    model: str = "sonnet",
    max_turns: int = 15,
    max_budget_usd: float = 2.00,
) -> WorkerResult:
    from .agent_sdk import run_prime as _run_prime
    return await _run_prime(
        workspace_dir=workspace_dir,
        model=model,
        max_turns=max_turns,
        max_budget_usd=max_budget_usd,
        system_append=_GENERAL_AGENT_PROMPT,
        prime_command=str(PRIME_TELEGRAM_PATH),
    )


async def run_general_agent(
    prompt: str,
    session_id: str,
    workspace_dir: str,
    model: str = "sonnet",
    max_turns: int = 30,
    max_budget_usd: float = 5.00,
) -> WorkerResult:
    from .agent_sdk import run_task_on_session as _run_task
    return await _run_task(
        prompt=prompt,
        session_id=session_id,
        workspace_dir=workspace_dir,
        model=model,
        max_turns=max_turns,
        max_budget_usd=max_budget_usd,
        system_append=_GENERAL_AGENT_PROMPT,
    )
