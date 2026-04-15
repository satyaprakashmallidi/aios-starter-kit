# Content Pipeline — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

<!-- MODULE METADATA
module: content-pipeline
version: v1
status: RELEASED
released: 2026-02-27
requires: [context-os, data-os]
phase: 4
category: ContentOS
complexity: medium-complex
api_keys: 0-1 (Notion is optional)
setup_time: 30-45 minutes
-->

---

## FOR CLAUDE

You are helping a user install Content Pipeline — their content intelligence system. This is a **workshop-driven install**, not just copying files. You are running an interactive Brand & Content Workshop that produces customized strategy documents, then installing the pipeline scripts and commands.

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("Strategy doc looks great — that's the foundation for everything!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps — if a check fails, stop and help the user fix it
- Use encouraging language throughout — they are building something real

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After Phase 1 (Foundation): "Pipeline foundation is ready. Now the fun part — let's figure out YOUR content strategy."
- After Phase 2 (Workshop): "Your strategy docs are locked in. Now let's wire up the commands."
- After Phase 3 (Commands): "Commands are live. Let's test the whole system end-to-end."
- After Phase 4 (Test): "It works! Here's what you just built and what to do next."

**Workshop approach (Phase 2):**
- This is INTERACTIVE. You are interviewing the user about their business, content, and audience.
- Read their ContextOS files first (`context/` folder) — use what you already know about their business.
- Ask questions in batches of 2-3, not rapid-fire 20 questions.
- After each workshop section, SHOW them what you wrote and get approval before moving on.
- If they already have a content strategy, adapt — don't force them to start from scratch.

**Error handling:**
- If Python version is too old → provide exact upgrade instructions for their OS
- If pip install fails → try: (1) upgrade pip, (2) install build tools, (3) specific fix
- If database init fails → check the data/ directory exists and has write permissions
- Never say "check the logs" — find the problem and explain it

---

## OVERVIEW

Content Pipeline turns your content chaos into a strategic system. Instead of staring at a blank page wondering what to create, you'll have a pipeline of ideas that are captured, classified, strategically developed, and scheduled — all powered by AI that understands your brand, audience, and business goals.

**What you get when it's done:**
- A content database that tracks every idea from raw capture to published
- Three slash commands: `/capture` (quick idea capture), `/develop` (full concept development with strategic positioning and packaging), `/schedule` (batch scheduling with date management)
- A 7-day context window that gives Claude awareness of your recent content, meetings, and pipeline state — so every idea it develops is informed and strategic
- Strategy documents that teach Claude your brand positioning, audience segments, content pillars, and offers
- For YouTube creators: a professional packaging strategy framework for crafting click-worthy titles and thumbnails
- Optional: Notion calendar sync for team-visible scheduling
- Optional: Telegram content capture via your CommandOS bot (if installed)

**Setup time:** 30-45 minutes (most of that is the Brand & Content Workshop — the actual install is quick)
**Running cost:** Free (Notion sync optional, also free)
**What you need:** ContextOS installed (so Claude knows your business), DataOS installed (for the database layer)

---

## SCOPING

Before installation, present the user with a choice:

**RECOMMENDED** (Smart defaults — works for most people)
- Full pipeline: database, 3 commands, context aggregator, pipeline renderer
- Interactive Brand & Content Workshop (Claude interviews you and writes your strategy docs)
- YouTube OR LinkedIn platform configuration
- Content capture via Claude Code (Telegram capture can be added later if CommandOS is installed)
- Estimated setup time: 30-45 minutes

**CUSTOM** (Walk through every option)
- Platform: YouTube / LinkedIn / Both (default: ask the user)
- Notion sync: Yes / No (default: No — add later if needed)
- Telegram capture topic: Yes / No (default: No — requires CommandOS)
- Workshop depth: Full interview / Quick setup from existing docs (default: Full interview)

Ask: "Want to go with RECOMMENDED, or would you like to walk through the options?"

If RECOMMENDED → ask only: "What's your primary content platform — YouTube or LinkedIn?"
If CUSTOM → walk through each option.

---

## PREREQUISITES

Check each prerequisite. Verify it works before proceeding.

### Python 3.10+
```bash
python3 --version
```
If not installed or too old: provide OS-specific install instructions.

### Claude Code CLI
```bash
claude --version
```

### ContextOS (Required)
Check that ContextOS is installed — the user should have a `context/` folder with their business context.
```bash
ls context/*.md 2>/dev/null | head -5
```
If no context files: "You need ContextOS installed first — it gives Claude your business context. Run that module first, then come back here."

### DataOS (Required)
Check that DataOS is installed — the user should have a `data/` directory.
```bash
ls data/*.db 2>/dev/null
```
If no database: "You need DataOS installed first — it provides the database layer. Run that module first, then come back here."

### Virtual Environment
```bash
ls .venv/bin/activate 2>/dev/null && echo "venv exists" || echo "no venv"
```
If no venv, they should have one from DataOS. If not:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

[VERIFY] All prerequisites show version numbers without errors.
Ask: "Everything checks out. Ready to start building?"

---

## PHASE 1: FOUNDATION

### Step 1: Install dependencies

```bash
source .venv/bin/activate
pip install python-dotenv requests
```

[VERIFY]
```bash
python3 -c "from dotenv import load_dotenv; import requests; print('Dependencies OK')"
```

### Step 2: Create the content database

Write `scripts/db.py` from the module's `scripts/db.py` file. Then initialize:

```bash
source .venv/bin/activate && python3 scripts/db.py
```

Expected: "Database initialized at: data/content.db" with 2 tables listed.

If the user's DataOS already created a data/ folder, the content.db will live alongside their main database. That's fine — the content pipeline uses its own database.

[VERIFY]
```bash
python3 scripts/db.py --check
```
Should show: content_ideas (0 rows), published_content (0 rows).

### Step 3: Install writer module

Write `scripts/writer.py` from the module's `scripts/writer.py` file.

[VERIFY]
```bash
source .venv/bin/activate && python3 scripts/writer.py
```
Expected: "Writer module loaded successfully."

### Step 4: Install context aggregator

Write `scripts/context_aggregator.py` from the module's `scripts/context_aggregator.py` file.

**Important:** The context aggregator automatically detects their DataOS database and pulls richer context (YouTube videos with transcripts, meeting summaries) if available. No configuration needed — it just works.

[VERIFY]
```bash
source .venv/bin/activate && python3 scripts/context_aggregator.py
```
Expected: Shows counts for recent content, meetings, and pipeline state.

### Step 5: Install pipeline renderer

Write `scripts/generate_pipeline.py` from the module's `scripts/generate_pipeline.py` file.

```bash
mkdir -p content
source .venv/bin/activate && python3 scripts/generate_pipeline.py
```

[VERIFY]
```bash
cat content/pipeline.md | head -5
```
Expected: Shows "# Content Pipeline" header with today's date.

After Phase 1: "Pipeline foundation is built — database, writer, context aggregator, and pipeline renderer are all live. Now the fun part — let's figure out YOUR content strategy."

---

## PHASE 2: BRAND & CONTENT WORKSHOP

This is the most important phase. You are running an interactive workshop to produce 3-4 strategy documents that teach Claude everything about the user's content business.

**Before starting:** Read the user's ContextOS files to understand their business:
```bash
ls context/
```
Read the relevant overview files. Use this knowledge throughout the workshop — don't ask questions you already know the answer to.

### Workshop Section 1: Platform & Strategy

Ask the user (adapt based on what you already know from ContextOS):

1. "What's your primary content platform?" (YouTube / LinkedIn — already confirmed during scoping)
2. "How often do you publish, or want to publish? What's your target cadence?"
3. "What are the 3-5 topic categories (content pillars) you create content about?"
4. "Who are your main competitors or peers in your space? How do you differentiate?"
5. "Any content rules you follow? (e.g., 'never hard-sell', 'always include examples')"
6. "How do you prefer to plan your schedule? Weekly batches, ad-hoc, fixed days?"

**After getting answers:** Write `content/strategy.md` using the `templates/strategy.md` template structure. Fill in everything from the conversation. Show the user the completed doc and ask: "Does this capture your strategy accurately? Anything to change?"

Wait for approval before continuing.

### Workshop Section 2: Brand & Audience

Ask the user:

1. "In one sentence, who are you and what do you do?" (their positioning)
2. "What gives you authority on your topic? What credentials, experience, or results do you have?"
3. "Describe your brand voice — formal or casual? Technical or accessible?"
4. "Let's define your audience segments. Who are the 3-5 distinct types of people you create for?"

For each audience segment, explore:
- Who they are (situation, mindset)
- What they want (desired outcome)
- What they need (what they actually need — often different)
- How to speak to them (language level)

5. "What proof points do you use to build trust? Numbers, results, testimonials?"

**After getting answers:** Write `content/brand-and-audience.md` using the template. Show the user and get approval.

### Workshop Section 3: Offers & Funnels

Ask the user:

1. "What do you sell? Walk me through your offers from free to highest-ticket."
2. "How does someone go from watching/reading your content to becoming a customer? What's the funnel?"
3. "How do you mention your offers in content? Do you pitch directly, or use a softer approach?"
4. "Are there any active campaigns or launches that affect what content you should create right now?"

**After getting answers:** Write `content/offers-and-funnels.md` using the template. Show the user and get approval.

### Workshop Section 4: Packaging Strategy (YouTube only)

If the user's primary platform is YouTube:

Tell them: "I'm going to install a packaging strategy framework — this teaches Claude how to craft click-worthy titles and thumbnails for every video. It's based on research into viral video psychology: the want-vs-need principle, the complementary system for titles + thumbnails, 10 viral title elements, thumbnail composition rules, and more."

Write `content/packaging-strategy.md` from the module's `templates/packaging-strategy.md` — this one is pre-written and doesn't need customization (it's a universal framework). But DO review it with the user:

"Here's the packaging strategy framework. It covers want-vs-need positioning, complementary title+thumbnail design, 10 viral elements, and composition rules. Want to read through it, or trust the framework and move on?"

### Workshop Summary

After all sections are complete:

```
Workshop complete! Here's what we built:

content/
├── strategy.md           — Your platform, cadence, pillars, competitive positioning
├── brand-and-audience.md — Your brand positioning and 3-5 audience segments
├── offers-and-funnels.md — Your offers, funnels, and content → revenue mapping
├── packaging-strategy.md — Title + thumbnail psychology framework (YouTube)
└── pipeline.md           — Auto-generated pipeline view (already live from Phase 1)
```

"These docs are what make your AI smart about YOUR content. Every time you run /develop, Claude reads these to position your content strategically. You can update them anytime as your business evolves."

---

## PHASE 3: COMMANDS & CAPTURE

### Step 1: Install /capture command

Write `.claude/commands/capture.md` from the module's `commands/capture.md` file.

Tell the user: "/capture is for quick idea capture — when you have a raw idea and want to classify it and store it as a stub. Think of it as dropping a note into your pipeline."

### Step 2: Install /develop command

Write `.claude/commands/develop.md` from the module's `commands/develop.md` file.

Tell the user: "/develop is the heavy hitter. It takes a stub and turns it into a full concept with strategic positioning, audience alignment, and platform-specific packaging. It loads a 7-day context window so it knows what you've recently published and what's in your pipeline."

### Step 3: Install /schedule command

Write `.claude/commands/schedule.md` from the module's `commands/schedule.md` file.

Tell the user: "/schedule helps you batch-plan your content calendar. It shows your developed ideas ranked by priority, you pick what to schedule with dates, and it calculates creation deadlines based on your format turnaround times."

### Step 4: Create concepts folder

```bash
mkdir -p content/concepts
```

This is where /develop saves full concept documents.

### Step 5: Telegram Content Capture (Optional — requires CommandOS)

Check if CommandOS is installed:
```bash
ls scripts/apps/command/bot.py 2>/dev/null && echo "CommandOS found" || echo "No CommandOS"
```

If CommandOS is installed, offer to set up a Content Capture topic:

"You have CommandOS installed. Want me to set up a Content Capture topic in your Telegram bot? This lets you capture content ideas from your phone — just send a message to the topic and Claude classifies it as a stub in your pipeline."

If yes: Guide the user through creating a forum topic in their Telegram group and adding the topic ID to their .env. The capture prompt should be configured to:
- Classify ideas using their content/strategy.md pillars and channels
- Check for duplicates against the content_ideas table
- Store as stubs with source_type='telegram'

If no CommandOS or user declines: "No problem — you can capture ideas anytime by running /capture in Claude Code."

[VERIFY] All 3 commands installed:
```bash
ls .claude/commands/capture.md .claude/commands/develop.md .claude/commands/schedule.md
```
Expected: All 3 files listed.

After Phase 3: "Commands are live. Let's test the whole system end-to-end."

---

## PHASE 4: TEST & EXTRAS

### Quick Test — Capture an Idea

Walk the user through capturing their first idea:

"Let's test the pipeline. Give me a content idea — anything you've been thinking about creating."

Run /capture with their idea. Verify:
- The idea was stored in the database
- The pipeline.md was regenerated and shows the new stub

### Full Test — Develop the Idea

"Now let's develop that stub into a full concept."

Run /develop with the stub ID. This exercises:
- Reading their strategy docs
- Building the 7-day context window
- Strategic positioning stage
- Packaging stage (titles + thumbnails for YouTube, hooks + visuals for LinkedIn)
- Writing to the database
- Generating the concept doc

Walk through the full /develop flow interactively. After it's complete:

"That's the full pipeline in action. You captured an idea, developed it with strategic positioning and packaging, and it's now sitting in your pipeline ready to schedule."

### Optional: Notion Sync

Ask: "Do you want to connect Notion for a team-visible content calendar? This is optional — everything works without it. It's useful if you have editors, thumbnail designers, or other team members who need to see the schedule."

If yes:

1. Guide them to create a Notion internal integration at https://www.notion.so/my-integrations
2. Save the token to their .env as NOTION_API_TOKEN
3. Find or create a Notion page where the database should live
4. Run the database creation:
   ```bash
   source .venv/bin/activate && python3 scripts/notion_sync.py --create-db PAGE_ID
   ```
5. Save the resulting database ID to .env as NOTION_PIPELINE_DB_ID
6. Test the connection:
   ```bash
   source .venv/bin/activate && python3 scripts/notion_sync.py --test
   ```

If no: "Got it — your pipeline.md and the database are your content calendar. You can always add Notion later."

### What You Built

Present the final summary:

```
Content Pipeline is live! Here's what's running:

Database:        data/content.db (content_ideas + published_content tables)
Strategy docs:   content/strategy.md, brand-and-audience.md, offers-and-funnels.md
Packaging:       content/packaging-strategy.md (YouTube framework)
Pipeline view:   content/pipeline.md (auto-regenerates)
Concept docs:    content/concepts/ (full developed concepts)

Commands:
  /capture  — Quick idea capture and classify
  /develop  — Full concept development with strategic positioning
  /schedule — Batch scheduling with date management

Context Window:
  The 7-day aggregator pulls your recent content, meetings, and pipeline
  state every time you run /develop — so Claude is always informed.
```

---

## WHAT'S NEXT

Now that Content Pipeline is running, here are your options:

1. **Start capturing ideas** — Run `/capture` whenever inspiration strikes, or message your Telegram Content Capture topic if you set one up. Build up a backlog of stubs.

2. **Develop your best ideas** — Run `/develop #ID` on your highest-potential stubs. Claude will position them strategically and craft platform-specific packaging.

3. **Schedule a content batch** — Once you have several developed ideas, run `/schedule` to plan your content calendar and calculate creation deadlines.

4. **Update your strategy** — Your strategy docs in `content/` are living documents. Update them as your brand, audience, or offers evolve. Claude reads them fresh every time.

5. **Thumbnail Generator** (coming soon) — Pairs with Content Pipeline. Takes your developed thumbnail concepts and generates actual thumbnails using AI image generation.

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
