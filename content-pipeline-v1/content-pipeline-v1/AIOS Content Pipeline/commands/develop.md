# /develop — Develop Content Concept

> Take a content idea stub and develop it into a fully strategized, packaged concept.

## Variables

$ARGUMENTS (the stub ID like "#5", or a raw idea to capture and develop in one go)

## Instructions

You are running the **Develop** step of the Content Pipeline. Your job is to take a captured idea and turn it into a fully developed content concept with strategic positioning, audience alignment, packaging, and offer mapping.

### Setup — Load Context

1. **Read the idea:**
   - If given an ID (#N): query `SELECT * FROM content_ideas WHERE id = N` via the content database
   - If given raw text: this is a new idea — capture it as a stub first (classify channel + format), then develop

2. **Read content strategy docs** (ALWAYS read these):
   - `content/strategy.md` — platform, cadence, pillars, personas, competitive positioning
   - `content/brand-and-audience.md` — brand positioning, target audience segments
   - `content/offers-and-funnels.md` — offers, funnels, audience → offer alignment, CTAs
   - `content/packaging-strategy.md` — title/thumbnail/hook frameworks (if it exists — YouTube users)

3. **Build the 7-day context window:**
   ```bash
   source .venv/bin/activate && python3 -c "
   import sys; sys.path.insert(0, '.')
   from scripts.context_aggregator import build_context_window, format_context_for_prompt
   context = build_context_window(days=7)
   print(format_context_for_prompt(context))
   "
   ```
   Read the output — this tells you:
   - Recent published content (what's already been covered)
   - Recent meetings (themes, discussions, insights)
   - Current pipeline state (what's already queued)

### Stage 1: STRATEGIC POSITIONING (Present and confirm)

Using the idea + context window + strategy docs, develop the strategic frame:

1. **Audience alignment** — Which of their defined segments does this serve? What problem does it solve for them?
2. **Authority angle** — Why is the creator THE voice on this topic? (Reference their brand positioning)
3. **Offer alignment** — Which offer does this drive toward? What's the CTA path? (Reference their offers-and-funnels.md)
4. **Narrative fit** — How does this connect to what they've been publishing recently? (Reference the context window)
5. **Funnel position** — awareness / consideration / conversion
6. **Content pillar** — Which of their defined pillars

**STOP. Present the strategic frame concisely. Ask: "Does this positioning feel right? Any angle changes?"**

### Stage 2: PACKAGING (Present and confirm)

The packaging stage adapts based on the user's primary platform.

#### For YouTube Users (packaging-strategy.md exists)

Use the full packaging strategy frameworks:

1. **3-5 title options** — Each using 2+ viral title elements from the packaging strategy. Include the element tags used (e.g., [curiosity + authority]).
2. **2-3 thumbnail concepts** — Each with:
   - Emotion (from the emotion mapping)
   - Text overlay (2-4 words, COMPLEMENTARY to title — different information)
   - Visual element (icon, screenshot, symbol)
   - Layout and type
3. **Hook strategy** — How title + thumbnail + opening 30 seconds work together. What's the curiosity gap? What's the promise?

#### For LinkedIn Users

1. **3-5 hook lines** — The first 1-2 lines that appear before "see more." Each should stop the scroll.
2. **Visual concept** — What image, carousel, or video thumbnail accompanies the post?
3. **Format recommendation** — Post, article, carousel, or video. With reasoning.
4. **Hashtag strategy** — 3-5 relevant hashtags

#### For All Platforms

- Ensure packaging is **complementary** — visual and text provide different information
- Reference the packaging strategy doc if available
- Consider what's trending and what gaps exist in recent content

**STOP. Present packaging options. Ask: "Which direction feels strongest? Any adjustments?"**

### Stage 3: STORE & FINALIZE

After the user confirms:

1. **Assign priority score (1-10):**
   - Strategic value (serves the business goals?)
   - Timeliness (news hook? trending topic?)
   - Demand signals (from context window — audience questions, meeting themes)
   - Production effort (format complexity, prep required)
   - Gap (not already covered recently)

2. **Write to database:**
   ```bash
   source .venv/bin/activate && python3 -c "
   import sys, json; sys.path.insert(0, '.')
   from scripts.db import get_connection
   from scripts.writer import write_developed_idea

   idea = {
       'id': EXISTING_ID_OR_NONE,
       'title': 'Selected primary title',
       'hook': 'Opening hook strategy',
       'description': 'Full concept description',
       'audience': 'Target audience description',
       'format_type': 'FORMAT',
       'channel': 'CHANNEL',
       'topics': 'comma,separated,topics',
       'source_type': 'develop',
       'title_options': json.dumps([
           {'text': 'Title A', 'elements': ['curiosity', 'authority']},
           {'text': 'Title B', 'elements': ['list', 'timeliness']},
       ]),
       'thumbnail_concepts': json.dumps([
           {'emotion': 'confidence', 'text_overlay': '2-4 words', 'visual': 'description'},
       ]),
       'funnel_position': 'awareness',
       'content_pillar': 'PILLAR',
       'audience_segment': 'SEGMENT',
       'offer_alignment': 'OFFER',
       'cta_path': 'CTA description',
       'proof_points': json.dumps([
           {'type': 'performance', 'text': 'Specific proof point'},
       ]),
       'authority_angle': 'Why you own this topic',
       'production_status': 'developed',
       'priority_score': 8,
       'research_json': json.dumps({'context_window': '7d'}),
       'developed_by': 'develop',
   }

   conn = get_connection()
   idea_id = write_developed_idea(conn, idea)
   conn.close()
   print(f'Saved as concept #{idea_id}')
   "
   ```

3. **Write concept doc:**
   Save the full concept to `content/concepts/{id}-{slug}.md` with all positioning, packaging, and strategy details.

4. **Regenerate pipeline:**
   ```bash
   source .venv/bin/activate && python3 scripts/generate_pipeline.py
   ```

5. **Report:**
   - Saved as concept #ID
   - Concept doc written to `content/concepts/`
   - Primary title/hook + channel + format
   - Priority score
   - "Ready for scheduling. Run /schedule when you want to plan your content calendar."

### Critical Rules

- **Interactive** — Present strategic positioning, wait for confirmation. Present packaging, wait for confirmation. Never blast through all stages.
- **Context-first** — Always reference what the 7-day context window tells you. "You posted about X on Tuesday, so this piece should angle toward Y."
- **Platform-appropriate** — Use the packaging frameworks that match their platform. Don't suggest thumbnails for LinkedIn posts.
- **Complementary packaging** — Title/hook and visual must provide DIFFERENT information.
- **Proof hierarchy** — Stack multiple proof types when available.
- **CTA alignment** — Every piece of content should have a clear path to an offer, even if subtle.

$ARGUMENTS
