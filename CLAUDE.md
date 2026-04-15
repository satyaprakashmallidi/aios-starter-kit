# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Is

This is an **AI Operating System workspace** for a freelance AI developer specializing in n8n automation, website building, and cloud integrations. Built on the AIOS framework from AAA Accelerator.

**This file (CLAUDE.md) is the foundation.** It is automatically loaded at the start of every session. Keep it current — it is the single source of truth for how Claude should understand and operate within this workspace.

> From the AAA Accelerator — the #1 AI business launch & AIOS program. [aaaaccelerator.com](https://aaaaccelerator.com)

---

## The Claude-User Relationship

Claude operates as an **agent assistant** with access to the workspace folders, context files, commands, and outputs. The relationship is:

- **User**: Defines goals, provides context about their role/function, and directs work through commands
- **Claude**: Reads context, understands the user's objectives, executes commands, produces outputs, and maintains workspace consistency

Claude should always orient itself through `/prime` at session start, then act with full awareness of who the user is, what they're trying to achieve, and how this workspace supports that.

---

## AIOS Mission

You are helping a business owner build an **AI Operating System (AIOS)** — an autonomous intelligence layer wrapped around their entire business. Everything in this workspace serves that goal.

### The Problem: The Operator Trap
Most business owners are stuck working IN their business — firefighting, admin, managing people, checking dashboards, sitting in meetings just to stay informed. 80% of bandwidth goes to "must-dos." Nothing left for growth, strategy, or the life they actually wanted. The old model says hire more people, buy more tools, work more hours. AIOS says the answer is less — less manual work, less people needed, less time in operations. More bandwidth for the work that matters.

### The Solution: Five Layers
The AIOS gives it back — one layer at a time:
1. **Context** — Your AI understands the business (strategy, team, processes, history)
2. **Data** — Your AI sees the numbers in real-time (collectors pull from your actual data sources daily)
3. **Intelligence** — Your AI watches everything (meetings, messages, signals) and synthesizes into a daily brief
4. **Automate** — Audit every task, score each one, automate them away one by one. Each task automated = bandwidth recovered.
5. **Build** — Freed bandwidth applied to growth, new initiatives, or life. Work ON the business, not IN it.

### Five Principles
1. **Just Ask** — If you can describe it in plain English, Claude can build it. Don't self-censor. Ask for the impossible.
2. **Talk, Don't Type** — Voice-first. Hold FN, speak for 60 seconds, let Claude format it. 3x faster than typing.
3. **Layers, Not Leaps** — One layer at a time. Each independently valuable. Through gradual exposure, you become technical without even trying.
4. **Build for Scale & Security** — Human-in-the-loop by default. Your data stays local. Plan before you build.
5. **Borrow Before You Build** — 80% modules, 20% custom. Check the library before building from scratch.

### Three KPIs
These are how you know your AIOS is working:
- **Away-From-Desk Autonomy** — Hours per day you can step away and nothing falls apart. Target: business runs while you sleep.
- **Task Automation %** — Percentage of recurring tasks automated. Use the Task Audit (`context/task-audit.md`) as your scoreboard.
- **Revenue Per Employee** — Total revenue ÷ team members. Not bigger companies — leaner, faster, more profitable ones.

### How You Should Help
- Be patient. Assume the user is non-technical unless told otherwise.
- Explain what you're doing in plain English BEFORE doing it.
- Celebrate wins — every module installed, every task automated is real progress toward freedom.
- When suggesting solutions, check existing modules and the community first (Borrow Before You Build).
- Keep the three KPIs in mind — every automation should move at least one KPI.
- Never dump error logs or technical jargon. Find the problem, explain it simply, fix it.

---

## Workspace Structure

```
.
├── CLAUDE.md                # This file — core context, always loaded
├── .env                     # API keys and credentials (gitignored, never commit)
├── .claude/
│   └── commands/            # Slash commands Claude can execute
│       ├── prime.md         # /prime — session initialization
│       ├── install.md       # /install — install an AIOS module
│       ├── create-plan.md   # /create-plan — create implementation plans
│       ├── implement.md     # /implement — execute plans
│       └── share.md         # /share — package systems for sharing
├── context/                 # Background context about the user and business
│   ├── business-info.md     # What the business does
│   ├── personal-info.md     # Who you are, your role
│   ├── strategy.md          # Current priorities and goals
│   ├── current-data.md      # Key metrics and current state
│   └── import/              # Drop documents here for Claude to analyze
├── module-installs/         # AIOS modules — drop module folders here, install with /install
├── plans/                   # Implementation plans created by /create-plan
├── outputs/                 # Work products and deliverables
├── reference/               # Templates, examples, reusable patterns, GTD methodology
├── scripts/                 # Automation scripts (added by modules)
├── gtd/                     # GTD system files (ProductivityOS)
├── outreach/                # Outbound outreach system (OutboundOS)
├── content/                 # Content creation system (Content Pipeline)
└── shares/                  # Packaged systems for sharing (created by /share)
```

**Key directories:**

| Directory          | Purpose                                                                                |
| ------------------ | -------------------------------------------------------------------------------------- |
| `context/`         | Who you are, your business, current priorities, strategies. Read by `/prime`.           |
| `context/group/`   | Auto-generated key-metrics.md — refreshed daily with live business data.              |
| `context/import/`  | Drop any docs here (business plans, ChatGPT exports, etc.) for Claude to analyze.      |
| `module-installs/` | AIOS modules go here. Install them with `/install module-installs/{module-name}`.      |
| `plans/`           | Detailed implementation plans. Created by `/create-plan`, executed by `/implement`.    |
| `outputs/`         | Deliverables, analyses, reports, and work products.                                    |
| `reference/`       | Helpful docs, templates, GTD methodology reference.                                      |
| `scripts/`         | Data collectors (collect_*.py) and automation scripts. Run: `python scripts/collect.py` |
| `gtd/`             | GTD system files — inbox, projects, next actions, dashboard (ProductivityOS).         |
| `outreach/`        | Outbound outreach — campaigns, dashboards, n8n templates (OutboundOS).                |
| `content/`         | Content pipeline — strategy docs, concepts, pipeline dashboard (Content Pipeline).   |
| `data/`            | SQLite databases — `data.db` (metrics), `data/intel.db` (meetings & messages).         |
| `shares/`          | Packaged systems for sharing. Created by `/share`, ready to hand off.                   |

---

## Context Summary

- **Business:** Freelance AI developer building n8n automations, websites, and cloud integrations for small businesses
- **Role:** Founder / AI Developer leading a team of 5
- **Current focus:** Expanding client base, landing bigger projects, leveling up skills
- **Key metric to watch:** Client growth and project pipeline

---

## Data Layer

All business metrics are collected daily into `data/data.db` (SQLite). Connected sources:
- **Bitrix24** — Tasks (CRM permissions needed for contacts/deals)
- **GitHub** — 30 repos, commits, issues
- **Vercel** — 20 deployments, projects
- **FX Rates** — Currency exchange rates

Run collection manually: `python scripts/collect.py`
Daily automation: Windows Task Scheduler runs at 6 AM automatically.

---

## ProductivityOS — GTD System

A complete Getting Things Done (GTD) system for managing work. Built on ContextOS.

**GTD files (all in `gtd/`):**
| File | Purpose |
|------|---------|
| `inbox.md` | Central capture bucket — everything goes here first |
| `projects.md` | Master project list (outcomes requiring 2+ actions) |
| `next-actions.md` | Next actions organized by context (@me, @claude, @calls, @team, @errands, @think, @record) |
| `waiting-for.md` | Delegated items with dates |
| `someday-maybe.md` | Incubated ideas — reviewed weekly |
| `areas.md` | Areas of responsibility (professional + personal) |
| `dashboard.md` | Operational hub — auto-refreshed counts and status |
| `review-checklist.md` | Weekly review protocol and trigger lists |

**Commands:**
- `/process` — Process the inbox to zero using the GTD decision tree
- `/review` — Guided weekly review (4 phases: Clear, Current, Creative, Rebuild)

**Scripts:**
- `python scripts/refresh_dashboard.py` — Refresh dashboard counts (runs automatically after /process or /review)
- `python scripts/inbox_writer.py "task"` — Capture a task to the inbox from CLI

**Reference:**
- `reference/gtd-methodology.md` — Full GTD methodology guide

---

## IntelOS — Intelligence Collection

Your AI gets ears. Every meeting and message is collected, classified, and searchable forever.

**Meeting sources connected:**
- **Fathom** — Meeting transcripts (API key needed in `.env`: `FATHOM_API_KEY`)
- **Bitrix** — CRM activities (calls/meetings) via existing webhook — no extra key needed

**Slack:** Not configured (skipped per boss's request).

**Database:** `data/intel.db` (SQLite)
- `meetings` — Transcripts and meeting records
- `slack_messages` — Slack messages (future)
- `staff_registry` — Team member registry for classification
- `collection_log` — Tracks collection runs

**Run collection manually:**
```
python scripts/intel/collect_all.py
```

**Query meetings directly:**
```sql
-- Show recent meetings
SELECT title, date, source, duration_minutes FROM meetings ORDER BY date DESC LIMIT 10;

-- Search meeting transcripts
SELECT title, date, substr(transcript_text, 1, 200) FROM meetings
WHERE transcript_text LIKE '%keyword%' ORDER BY date DESC;
```

**Collection runs automatically daily** at 6 AM via Windows Task Scheduler (`AIOS-IntelOS-DailyCollect`).

---

## OutboundOS — WhatsApp + Gmail Outreach

AI-powered outbound lead generation. Your AI manages the outreach pipeline — from first message to follow-up to Bitrix24.

**Outreach files (all in `outreach/`):**
| File | Purpose |
|------|---------|
| `outreach/campaigns.md` | Track all outreach campaigns — leads, status, stats |
| `outreach/dashboard.md` | Quick stats — campaigns, replies, conversions |
| `outreach/config.md` | n8n webhook URLs + your personal info (fill this in first) |
| `outreach/templates/whatsapp-intro.md` | WhatsApp first message template |
| `outreach/templates/gmail-followup.md` | Gmail follow-up template |
| `outreach/leads/` | Drop lead lists here (CSV or markdown) |

**Commands:**
- `/start-outreach` — Start a new outreach campaign (you provide the lead list)

**How it works:**
1. You find leads (LinkedIn, referrals, any source)
2. Give the list to Claude with `/start-outreach`
3. Claude sends personalized WhatsApp messages via your n8n workflow
4. Claude logs each lead to Bitrix24 automatically
5. After 3 days with no reply, Claude reminds you to send Gmail follow-ups

**Setup required:** Fill in `outreach/config.md` with your n8n webhook URLs before first use.

---

## Content Pipeline — Content Creation System

Full content lifecycle for YouTube, LinkedIn, and more. Capture ideas, develop concepts with strategic positioning, and schedule your content calendar.

**Content files (all in `content/`):**
| File | Purpose |
|------|---------|
| `content/pipeline.md` | Auto-generated dashboard — your full pipeline at a glance |
| `content/concepts/` | Full concept documents (created by `/develop`) |
| `content/strategy.md` | Platform, cadence, content pillars (set up in workshop) |
| `content/brand-and-audience.md` | Brand positioning + audience segments |
| `content/offers-and-funnels.md` | Offers, funnels, CTAs |
| `content/packaging-strategy.md` | YouTube title/thumbnail framework |

**Commands:**
- `/capture [idea]` — Quick idea capture + classification
- `/develop [#id]` — Full concept development (titles, thumbnails, hooks)
- `/schedule` — Batch scheduling with publish/film dates

**Database:** `data/content.db` (SQLite)

**Setup required:** Run the Brand & Content Workshop to fill in your strategy documents.

---

## CommandOS — Telegram AI Assistant

Your AI assistant on your phone, powered by Claude Code. Messages from your Telegram group dispatch AI agents with full workspace access.

**Currently running:** `PYTHONIOENCODING=utf-8 python -m apps.command.main`
**Startup script:** `run-telegram-bot.bat`

**Bot commands:**
| Command | Where | What it does |
|---------|-------|---------------|
| `/new` | General | Spawn a fresh Sonnet agent in a new topic |
| `/new opus` | General | Spawn a fresh Opus agent (more capable) |
| `/name` | Any agent topic | Rename the topic based on your conversation |
| `/compact` | Any agent topic | Compress context when the agent starts forgetting |
| `/reset` | Any agent topic | Clear the session and start fresh |
| `/help` | General | Show the command list |
| `/reboot` | Anywhere | Restart the bot process |
| `/cost` | General | Show today's API usage cost |

**Features:**
- Persistent conversations survive bot restarts
- Photo/screenshot analysis
- PDF report generation (WeasyPrint)
- Chart/data visualization (matplotlib)
- Voice notes skipped (needs OpenAI key)

**Always-on setup:** Run `scripts/create-bot-task.ps1` as Administrator to set up Windows Task Scheduler.

---

## Thumbnail Generator — AI YouTube Thumbnails

AI-powered YouTube thumbnail generation using Gemini 3 Pro. Creates 4 professional thumbnail concepts per video, composited with your reference photos for consistent face likeness.

**Thumbnail folders:**
| Folder | Purpose |
|--------|---------|
| `thumbnails/` | Root folder |
| `thumbnails/photos/` | Your reference photos for thumbnail generation |
| `thumbnails/photo-catalog/` | Auto-classified photo library |
| `thumbnails/outputs/` | Generated thumbnails |
| `thumbnails/brand-rules.md` | Your visual style rules |

**Commands:**
- `/thumbgen [video topic]` — Generate 4 thumbnail concepts with 2x2 comparison grid

**Scripts:**
- `python scripts/generate_thumbnail.py --topic "..."` — Generate single thumbnail
- `python scripts/photo_selector.py --emotion surprised` — Select photos by emotion/expression
- `python scripts/analyze_photos.py --scan thumbnails/photos/` — Scan and classify your photo library
- `python scripts/combine_thumbnails.py` — Create 2x2 comparison grid
- `python scripts/search_examples.py --topic "..."` — Research competitor thumbnails

**Photo Classification:**
Add photos to `thumbnails/photos/`, then run:
```
python scripts/analyze_photos.py --scan thumbnails/photos/
```
This classifies photos by expression (confident, surprised, thinking, happy, serious), pose (close-up, medium, full-body), and setting (office, home, outdoor, laptop, whiteboard).

**API Keys required:**
- `GOOGLE_API_KEY` — Gemini image generation (get yours: https://aistudio.google.com/apikey)
- `SCRAPECREATORS_API_KEY` — YouTube competitor research (optional, get yours: https://scrape-creators.com)

**Setup required:** Fill in `thumbnails/brand-rules.md` with your visual style before first use.

---

## Commands

### /start-outreach

**Purpose:** Start a new outbound WhatsApp + Gmail outreach campaign.

You provide a lead list (names, WhatsApp numbers, companies, context), and Claude:
1. Personalizes WhatsApp messages using your template
2. Triggers your n8n WhatsApp workflow to send messages
3. Logs each lead to Bitrix24
4. Schedules Gmail follow-up reminders for leads who don't reply

**Before using:** Fill in `outreach/config.md` with your n8n webhook URLs.

Example: `/start-outreach` — then paste your lead list when prompted.

### /capture [idea]

**Purpose:** Capture a content idea and add it to your pipeline.

You just describe the idea in plain English. Claude classifies it by channel, format, and content pillar, checks for duplicates, and stores it as a stub ready for development.

Example: `/capture I had an idea about automated reporting for small businesses`

### /develop [#id]

**Purpose:** Develop a captured idea into a full content concept.

Takes a stub and develops it with:
- Strategic positioning (audience, authority angle, offer alignment)
- 3-5 title options with viral elements (YouTube)
- 2-3 thumbnail concepts (YouTube)
- Hook strategy
- CTA path

Uses your 7-day context window (recent content, meetings, pipeline state) to make every concept strategically informed.

Example: `/develop #12`

### /schedule

**Purpose:** Interactive batch scheduling session.

Shows your developed ideas ranked by priority, helps you pick what to schedule, calculates film-by dates, and optionally pushes to Notion calendar.

Example: `/schedule` — or `/schedule review` to check current schedule.

### /thumbgen [video topic]

**Purpose:** Generate 4 AI thumbnail concepts for a YouTube video.

Creates professional thumbnails using Gemini 3 Pro Image Preview, composited with your reference photos for accurate face likeness. Produces a 2x2 comparison grid for easy selection.

Example: `/thumbgen "n8n automation workflow setup"` or `/thumbgen n8n API integration`

### /process

**Purpose:** Process the GTD inbox to zero using the GTD decision tree.

Walks through each captured item, asks the right questions, and routes each to the correct GTD file (projects, next-actions, waiting-for, someday/maybe, or trash). After processing, runs `refresh_dashboard.py` to update the dashboard.

Example: Run `/process` whenever you want to work through your inbox.

### /review

**Purpose:** Guided weekly review using GTD methodology.

Runs through 4 phases: GET CLEAR (empty all inboxes), GET CURRENT (update all lists), GET CREATIVE (scan areas and someday/maybe), REBUILD (refresh dashboard). Target: 30-60 minutes. Fridays recommended.

Example: Run `/review` at the end of each week to keep your GTD system trustworthy.

### /install [module-path]

**Purpose:** Install an AIOS module into this workspace.

Point it at a module folder in `module-installs/` and Claude walks you through the guided setup. Each module adds a new capability to your AIOS.

Example: `/install module-installs/context-os`

### /prime

**Purpose:** Initialize a new session with full context awareness.

Run this at the start of every session. Claude will:

1. Read CLAUDE.md and context files
2. Summarize understanding of the user, workspace, and goals
3. Confirm readiness to assist

### /create-plan [request]

**Purpose:** Create a detailed implementation plan before making changes.

Use when adding new functionality, commands, scripts, or making structural changes. Produces a thorough plan document in `plans/` that captures context, rationale, and step-by-step tasks.

Example: `/create-plan add a competitor analysis command`

### /implement [plan-path]

**Purpose:** Execute a plan created by /create-plan.

Reads the plan, executes each step in order, validates the work, and updates the plan status.

Example: `/implement plans/2026-01-28-competitor-analysis-command.md`

### /update-data

**Purpose:** Run data collection manually to refresh metrics.

Runs `python scripts/collect.py` to pull fresh data from all connected sources (Bitrix, GitHub, Vercel) and regenerate `key-metrics.md`. Useful if you want up-to-date numbers before a session.

---

### /share [system or feature]

**Purpose:** Package a system or feature from your workspace for sharing.

Deep-dives the code first to fully understand it, then produces a self-contained, beginner-friendly package with a Claude-guided installer (INSTALL.md + README.md + scripts). The recipient gives the folder to Claude Code and says "read INSTALL.md and set this up" — Claude walks them through everything step by step. Runs a 6-stage interactive flow: Research → Scope → Frame → Write → Validate → Deliver. Outputs to `shares/`.

Example: `/share the daily brief system`

---

## Getting Started

**First time?** Start here:

1. Run `/prime` — verify Claude knows your business (ContextOS, DataOS, IntelOS, ProductivityOS, OutboundOS already installed)
2. Run `/update-data` to refresh your metrics on demand
3. Run `python scripts/intel/collect_all.py` to pull meeting intelligence
4. Run `/process` to clear your inbox and start using GTD
5. Install more modules from `module-installs/` as you're ready

**Returning?** Run `/prime` at the start of every session.

---

## Critical Instruction: Maintain This File

**Whenever Claude makes changes to the workspace, Claude MUST consider whether CLAUDE.md needs updating.**

After any change — adding commands, scripts, workflows, or modifying structure — ask:

1. Does this change add new functionality users need to know about?
2. Does it modify the workspace structure documented above?
3. Should a new command be listed?
4. Does context/ need new files to capture this?

If yes to any, update the relevant sections. This file must always reflect the current state of the workspace so future sessions have accurate context.

---

## Session Workflow

1. **Start**: Run `/prime` to load context
2. **Work**: Use commands or direct Claude with tasks
3. **Install modules**: Use `/install` to add new AIOS capabilities
4. **Plan changes**: Use `/create-plan` before significant additions
5. **Execute**: Use `/implement` to execute plans
6. **Share**: Use `/share` to package systems for team, clients, or community
7. **Maintain**: Claude updates CLAUDE.md and context/ as the workspace evolves

---

## Notes

- Keep context minimal but sufficient — avoid bloat
- Plans live in `plans/` with dated filenames for history
- Outputs are organized by type/purpose in `outputs/`
- Reference materials go in `reference/` for reuse
- API keys go in `.env` — never commit this file

<!-- convex-ai-start -->
This project uses [Convex](https://convex.dev) as its backend.

When working on Convex code, **always read `convex/_generated/ai/guidelines.md` first** for important guidelines on how to correctly use Convex APIs and patterns. The file contains rules that override what you may have learned about Convex from training data.

Convex agent skills for common tasks can be installed by running `npx convex ai-files install`.
<!-- convex-ai-end -->
