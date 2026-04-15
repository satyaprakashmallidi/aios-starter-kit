# Diagram Engine — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

<!-- MODULE METADATA
module: diagram-engine
version: v1
status: RELEASED
released: 2026-02-27
requires: []
phase: 4
category: Utility
complexity: simple
api_keys: 0
setup_time: 5-10 minutes
-->

---

## FOR CLAUDE

You are helping a user install the Diagram Engine AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("D2 installed — that's the only tool we need. The rest is just files!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps — if a check fails, stop and help the user fix it
- Use encouraging language throughout — they are building something real

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "We've got everything we need. Ready to start building?"
- After installation: "It's installed. Let's test it."
- After test: "It works! Here's what you just built and what you can do with it."

**Error handling:**
- If D2 install fails via brew → try the curl installer instead
- If D2 install fails via curl → check if they have write access to /usr/local/bin
- If render fails → check D2 version (needs 0.7.0+), check the .d2 file has valid syntax
- Never say "check the logs" — find the problem and explain it

---

## OVERVIEW

The Diagram Engine lets you generate professional architecture diagrams just by describing what you want in plain English. You say "create a diagram of my data pipeline" and Claude writes a text-based source file, renders it to a PNG image, checks it visually, and keeps iterating until it looks right.

No design tools. No drag-and-drop. No Figma or Canva. Just describe what you need and Claude handles the rest.

The diagrams are text files that live in your project — they're version-controlled, diffable, and easy to update. Every time your system changes, you can just ask Claude to update the diagram.

**What you'll have when done:** A `diagrams/` folder in your workspace, a render script, and a Claude Code skill that knows how to write D2 diagrams with 5 design patterns, 3 color palettes, and professional conventions.

**Setup time:** 5-10 minutes
**Cost:** Free — everything runs locally, no API keys needed

---

## SCOPING

**RECOMMENDED** (Smart defaults — fastest path)
- D2 CLI installed
- Render script in `scripts/`
- Diagram skill active in `.claude/skills/`
- Empty `diagrams/` folder ready to go

Estimated setup time: 5-10 minutes

**CUSTOM** (Walk through options)
- Skill install location: project-level `.claude/skills/` (default) vs user-level `~/.claude/skills/` (available in all projects)
- D2 theme: Neutral Default (0), Origami/hand-drawn (100), or others

Ask: "Want to go with RECOMMENDED, or would you like to walk through the options?"

If RECOMMENDED → proceed with project-level skill, Neutral Default theme.
If CUSTOM → walk through each option.

---

## PREREQUISITES

### D2 CLI

D2 is the open-source tool that turns text files into diagram images. Check if it's already installed:

```bash
d2 --version
```

If not installed, install it:

**macOS:**
```bash
brew install d2
```

**Linux:**
```bash
curl -fsSL https://d2lang.com/install.sh | sh -
```

**Windows (via scoop):**
```bash
scoop install d2
```

[VERIFY]
```bash
d2 --version
```
Expected: Version 0.7.0 or higher. If the version shows, D2 is ready.

Ask: "D2 is installed. That's the only tool we need — no API keys, no accounts, nothing else. Ready to set it up?"

---

## INSTALL

### Step 1: Create the diagrams folder

This is where your diagram source files and rendered PNGs will live.

```bash
mkdir -p diagrams
```

### Step 2: Create the render script

This script auto-discovers all `.d2` files in `diagrams/` and renders them to PNG in one command.

Create `scripts/generate_diagrams.sh` with this content:

```bash
#!/usr/bin/env bash
# Render all D2 diagram source files to PNG.
# Usage: bash scripts/generate_diagrams.sh [layout] [theme]
#
# Layout engines:
#   elk   — Eclipse Layout Kernel (cleaner hierarchical layouts, recommended)
#   dagre — Default D2 engine (faster, good for simple diagrams)
#
# Themes (built-in):
#   0 — Neutral Default (clean, professional)
#   1 — Neutral Grey
#   3 — Flagship Terrastruct
#   4 — Cool Classics
#   5 — Mixed Berry Blue
#   6 — Grape Soda
#   100 — Origami (hand-drawn look)
#
# Requires: d2 (https://d2lang.com)
#   macOS:  brew install d2
#   Linux:  curl -fsSL https://d2lang.com/install.sh | sh -

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DIAGRAM_DIR="$ROOT_DIR/diagrams"

LAYOUT="${1:-elk}"
THEME="${2:-0}"

if ! command -v d2 &> /dev/null; then
    echo "ERROR: d2 is not installed."
    echo "  macOS:  brew install d2"
    echo "  Linux:  curl -fsSL https://d2lang.com/install.sh | sh -"
    echo "  More:   https://d2lang.com"
    exit 1
fi

if [ ! -d "$DIAGRAM_DIR" ]; then
    echo "ERROR: diagrams/ directory not found at $DIAGRAM_DIR"
    echo "  Create it: mkdir -p diagrams"
    exit 1
fi

echo "Rendering diagrams (layout=$LAYOUT, theme=$THEME)..."
echo ""

count=0
errors=0

for d2_file in "$DIAGRAM_DIR"/*.d2; do
    [ -f "$d2_file" ] || continue
    basename=$(basename "$d2_file" .d2)
    png_file="$DIAGRAM_DIR/${basename}.png"

    echo -n "  $basename.d2 → $basename.png ... "
    if d2 --layout "$LAYOUT" --theme "$THEME" --pad 40 "$d2_file" "$png_file" 2>/dev/null; then
        size=$(ls -lh "$png_file" | awk '{print $5}')
        echo "OK ($size)"
        ((count++))
    else
        echo "FAILED"
        ((errors++))
    fi
done

echo ""
if [ $count -eq 0 ] && [ $errors -eq 0 ]; then
    echo "No .d2 files found in diagrams/"
else
    echo "Done: $count rendered, $errors errors"
fi
```

Then make it executable:

```bash
chmod +x scripts/generate_diagrams.sh
```

[VERIFY]
```bash
bash scripts/generate_diagrams.sh
```
Expected: "No .d2 files found in diagrams/" — this is correct because we haven't created any diagrams yet.

### Step 3: Install the diagram skill

This is the brain of the system — a reference file that teaches Claude how to write D2 diagrams with professional patterns, color palettes, and conventions.

Create the skill directory:

```bash
mkdir -p .claude/skills/d2-diagrams
```

Now read the `SKILL.md` file that came with this module (it's in the same folder as this INSTALL.md). Copy its entire contents into `.claude/skills/d2-diagrams/SKILL.md` in the user's workspace.

[VERIFY]
```bash
ls .claude/skills/d2-diagrams/SKILL.md
```
Expected: The file path prints without error.

### Step 4: Create a starter diagram

Let's create a simple test diagram so we can verify everything works end to end.

Create `diagrams/my-system.d2`:

```d2
direction: right

title: |md
  # My First Diagram
| {near: top-center; shape: text; style.font-size: 28; style.bold: true}

user: User {
  shape: person
  style.fill: "#6b7280"
  style.font-color: "#ffffff"
}

app: Web App {
  style.fill: "#2563eb"
  style.font-color: "#ffffff"
  style.bold: true
}

db: Database {
  shape: cylinder
  style.fill: "#1a1a2e"
  style.font-color: "#ffffff"
}

user -> app: uses
app -> db: reads/writes
```

---

## TEST

### Quick test — render the starter diagram

```bash
bash scripts/generate_diagrams.sh
```

Expected output:
```
Rendering diagrams (layout=elk, theme=0)...

  my-system.d2 → my-system.png ... OK (XXK)

Done: 1 rendered, 0 errors
```

### Visual validation — check the output

Read the rendered PNG at `diagrams/my-system.png` to verify it looks correct. You should see three boxes connected by arrows: a person shape (User), a blue rectangle (Web App), and a dark cylinder (Database).

If test works: "It works! You just created your first architecture diagram. The file `diagrams/my-system.d2` is the text source — you can edit it anytime. The PNG is the rendered output. From now on, just ask me to create or update diagrams and I'll handle everything."

If render fails:
1. Check D2 is installed: `d2 --version` (needs 0.7.0+)
2. Check the .d2 file exists: `ls diagrams/my-system.d2`
3. Try rendering directly: `d2 --layout elk --theme 0 --pad 40 diagrams/my-system.d2 diagrams/my-system.png` — this will show the actual error message

---

## WHAT'S NEXT

Now that the Diagram Engine is running, here are your options:

1. **Create your first real diagram** — Ask Claude: "Create a diagram showing my business structure" or "Diagram my data pipeline" or "Map out my automation schedule." Claude will write the D2 file, render it, check it visually, and iterate.

2. **Try different themes** — Run `bash scripts/generate_diagrams.sh elk 100` for a hand-drawn Origami look, or `elk 6` for Grape Soda. The SKILL.md has all available themes listed.

3. **Explore the 5 design patterns** — The skill includes patterns for: Simple Flow (pipelines), Hub-and-Spoke (architecture), Multi-Layer (complex systems), Before/After (comparisons), and Funnel (hierarchies). Ask Claude to use a specific pattern.

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
