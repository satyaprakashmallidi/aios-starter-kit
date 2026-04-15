# Diagram Engine

> Turn natural language into professional architecture diagrams — Claude writes, renders, and visually validates them for you.

## What This Does

- Generate architecture diagrams, flowcharts, system maps, data flows, org charts, and funnels from plain English descriptions
- Claude writes the source file, renders it to PNG, checks it visually, and iterates until it looks right
- Text-based source files live in git — diffable, versionable, no design tools needed
- Includes 5 design patterns and 3 color palettes for professional results

## What You Need

- A computer (Mac, Linux, or Windows)
- Claude Code installed
- D2 CLI installed (free, open source — `brew install d2`)

## How to Install

1. Give this folder to Claude Code
2. Say: "Read INSTALL.md and help me set this up"
3. Follow along — Claude handles everything

**Estimated setup time:** 5-10 minutes

## Running Cost

Free — everything runs locally. No API keys, no external services, no subscriptions.

## What's Inside

| File | Purpose |
|------|---------|
| `INSTALL.md` | Installation guide (Claude reads this) |
| `SKILL.md` | D2 language reference, patterns, palettes — installed as a Claude Code skill |
| `scripts/generate_diagrams.sh` | Batch render script — all `.d2` → `.png` in one command |

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
