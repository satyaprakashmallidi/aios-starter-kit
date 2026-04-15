# Thumbnail Generator

> Generate professional YouTube thumbnails with AI — your face, your brand, 4 concepts in minutes.

## What This Does

- Generates 4 distinct AI thumbnail concepts for any video topic using Gemini image generation
- Uses intelligent multi-photo reference selection (Primary + Supporting strategy) for accurate face likeness
- Researches high-performing competitor thumbnails on YouTube as style inspiration
- Creates a 2x2 comparison grid for quick concept selection
- Supports iterative refinement — pick a direction, refine, repeat
- Auto-injects your brand style guide into every generation for consistent thumbnails

## What You Need

- A computer (Mac or Linux)
- Claude Code installed
- Google account (for Gemini API key — free tier available)
- Scrape Creators account ($29/month — for YouTube thumbnail research)
- 10-30 photos of yourself (various expressions, angles, outfits)

## How to Install

1. Give this folder to Claude Code
2. Say: "Read INSTALL.md and help me set this up"
3. Follow along — Claude handles everything

**Estimated setup time:** 30-45 minutes (photo classification is the bulk)

## Running Cost

- **Gemini API:** Free tier is generous for thumbnail generation. Paid tier if you exceed limits.
- **Scrape Creators:** $29/month for 10,000 credits (each YouTube search uses ~1 credit)
- **Total:** $0-30/month depending on volume

## What's Inside

| File | Purpose |
|------|---------|
| `INSTALL.md` | Installation guide (Claude reads this) |
| `scripts/generate_thumbnail.py` | Core Gemini image generation engine |
| `scripts/photo_selector.py` | Intelligent photo selection algorithm |
| `scripts/analyze_photos.py` | Photo catalog scanner + optimizer |
| `scripts/combine_thumbnails.py` | 2x2 comparison grid compositor |
| `scripts/search_examples.py` | YouTube competitor thumbnail research |
| `scripts/requirements.txt` | Python dependencies |
| `scripts/.env.example` | API key template |
| `templates/brand-style.md` | Brand style template (you customize) |
| `.claude/commands/thumbgen.md` | /thumbgen slash command |
| `.claude/skills/thumbgen/SKILL.md` | Full workflow + psychology framework |

## How It Works

The system uses a **multi-photo reference strategy** instead of a single headshot. For each thumbnail concept, it:

1. Selects 3-5 photos of you (1 primary matching the desired expression + supporting photos from different angles)
2. Interleaves text labels between the photos ("PRIMARY: confident smile, front angle")
3. Prepends your identity description to the prompt
4. Appends your brand style guide
5. Sends everything to Gemini with a detailed concept prompt

This approach dramatically improves face likeness compared to single-photo methods.

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
