# Thumbnail Generator — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

<!-- MODULE METADATA
module: thumbnail-generator
version: v1
status: RELEASED
released: 2026-02-27
requires: []
phase: 4
category: ContentOS
complexity: medium
api_keys: 2
setup_time: 30-45 minutes
-->

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("API key verified — nice, that's the hardest part done!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps — if a check fails, stop and help the user fix it
- Use encouraging language throughout — they are building something real

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "We've got everything we need. Ready to start building?"
- After API keys: "All keys verified. The boring part is done — now the fun stuff."
- After photo setup: "Your photo catalog is ready. This is where the magic starts."
- After installation: "It's installed. Let's test it."
- After test: "It works! Here's what you just built and what you can do with it."

**Error handling:**
- If Python version is too old → provide exact upgrade instructions for their OS
- If an API key is invalid → walk them through getting a new one step by step
- If pip install fails → try: (1) upgrade pip, (2) install build tools, (3) specific fix
- If any command fails → explain what went wrong in one sentence, then provide the fix
- Never say "check the logs" — find the problem and explain it

---

## OVERVIEW

This module gives you an AI-powered YouTube thumbnail generator. Instead of spending hours in Photoshop or paying $50-100+ per thumbnail, you'll generate 4 professional thumbnail concepts in minutes — all using YOUR face, YOUR brand, and proven thumbnail psychology.

**What you'll have when it's done:**
- A `/thumbgen` command in Claude Code that generates 4 distinct thumbnail concepts for any video topic
- An intelligent photo selection system that picks the best reference photos for each concept
- YouTube competitor research that downloads high-performing thumbnails as style inspiration
- A 2x2 comparison grid so you can quickly pick the best direction
- Iteration support — refine and perfect your chosen thumbnail

**How it works:** The system uses Gemini's image generation with a multi-photo reference strategy (not just one headshot). It sends 3-5 photos of you from different angles with text labels, which dramatically improves face likeness compared to single-photo approaches. Your brand style guide auto-injects into every generation for consistent thumbnails.

**Setup time:** ~30-45 minutes (the photo classification step takes the most time)

**Running cost:** Gemini API has a generous free tier for image generation. Scrape Creators API starts at $29/month for YouTube research. Total: ~$0-30/month depending on volume.

---

## SCOPING

Before installation, present the user with a choice:

**RECOMMENDED** (Smart defaults — fastest path, works for most people)
- Full thumbnail generator with all 5 scripts
- Both API keys (Gemini + Scrape Creators)
- Photo catalog setup with guided classification
- Generic brand style template (customize later)
- Estimated setup time: 30 minutes

**CUSTOM** (Walk through every option together)
- Choose which scripts to include
- Option to skip Scrape Creators API (no competitor research — not recommended)
- Option to set up brand style in detail during install (adds 15 min)
- Option to classify all photos now vs. just the essentials (5 vs. 10-30)

Ask: "Want to go with RECOMMENDED, or would you like to walk through the options?"

If RECOMMENDED → proceed with defaults, briefly note what was chosen.
If CUSTOM → walk through each option, explain trade-offs, let them choose.

---

## PREREQUISITES

Check each prerequisite. Verify it works before proceeding to the next.

### Python 3.10+
```bash
python3 --version
```
If not installed or too old:
- **macOS:** `brew install python` (requires Homebrew: https://brew.sh)
- **Linux:** `sudo apt install python3.11` (Ubuntu/Debian) or `sudo dnf install python3.11` (Fedora)
- **Windows:** Download from https://python.org/downloads

### Claude Code CLI
```bash
claude --version
```
If not installed:
```bash
npm install -g @anthropic-ai/claude-code
```
If npm is not installed, install Node.js first:
- **macOS:** `brew install node`
- **Linux:** `sudo apt install nodejs npm`
- **Windows:** Download from https://nodejs.org

[VERIFY] Both commands should show version numbers without errors.
Ask: "Everything checks out. Ready to move on to API keys?"

---

## API KEYS

Collect each API key one at a time. Verify each before moving to the next.

### Google Gemini API Key [required]

This powers the AI image generation — it's the core of the whole system.

1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Select any Google Cloud project (or create a new one — it's free)
5. Copy the key (it starts with `AIza` and is about 39 characters long)
6. Paste it here — I'll save it securely in your .env file

[VERIFY]
```bash
python3 -c "
from google import genai
import os
client = genai.Client(api_key='PASTE_KEY_HERE')
models = client.models.list()
print('Gemini API key verified — connected successfully')
"
```
Expected: "Gemini API key verified — connected successfully"
If it fails: The key might be wrong — go back to https://aistudio.google.com/apikey and create a new one. Make sure you copied the full key.

### Scrape Creators API Key [required]

This lets you search YouTube for high-performing thumbnails in your niche — studying what works dramatically improves your results.

1. Go to https://scrapecreators.com
2. Create an account and choose a plan (starts at $29/month for 10,000 credits)
3. After signing in, go to your dashboard
4. Find your API key (usually on the main dashboard page or under Settings/API)
5. Copy the key
6. Paste it here — I'll save it in your .env file

[VERIFY]
```bash
python3 -c "
import urllib.request, json
req = urllib.request.Request(
    'https://api.scrapecreators.com/v1/youtube/search?query=test&includeExtras=true',
    headers={'x-api-key': 'PASTE_KEY_HERE'}
)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
print(f'Scrape Creators API verified — found {len(data.get(\"videos\", []))} videos')
"
```
Expected: "Scrape Creators API verified — found X videos"
If it fails: Check that your account has credits remaining. The key should be copied exactly from your dashboard.

After all keys are collected: "All keys verified. The setup part is done — now we build."

---

## INSTALL

Follow each step in order. Verify before moving to the next.

### Step 1: Create the project folder

```bash
mkdir -p ~/thumbnail-generator
cd ~/thumbnail-generator
```

### Step 2: Set up Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Note: On Windows, use `.venv\Scripts\activate` instead.

### Step 3: Install dependencies

Write `scripts/requirements.txt`:
```
google-genai>=1.0.0
Pillow>=10.0.0
pillow-avif-plugin>=1.4.0
python-dotenv>=1.0.0
```

Then install:
```bash
mkdir -p scripts
# (write requirements.txt with the contents above)
pip install -r scripts/requirements.txt
```

[VERIFY]
```bash
python3 -c "from google import genai; from PIL import Image; from dotenv import load_dotenv; print('Dependencies OK')"
```

### Step 4: Configure environment

Write the `.env` file using the API keys collected above:
```
GOOGLE_API_KEY=<their key>
SCRAPECREATORS_API_KEY=<their key>
```

[VERIFY]
```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Config OK:', bool(os.getenv('GOOGLE_API_KEY')), bool(os.getenv('SCRAPECREATORS_API_KEY')))"
```
Expected: `Config OK: True True`

### Step 5: Create the scripts

Write all 5 scripts to the `scripts/` folder. The complete source code for each script is included in this module package at `scripts/`. Copy each file:

1. `scripts/generate_thumbnail.py` — Core Gemini image generation engine
2. `scripts/photo_selector.py` — Intelligent photo selection algorithm
3. `scripts/analyze_photos.py` — Photo catalog scanner and optimizer
4. `scripts/combine_thumbnails.py` — 2x2 comparison grid compositor
5. `scripts/search_examples.py` — YouTube competitor thumbnail research

Read each file from this module package and write it to the user's project.

[VERIFY]
```bash
ls scripts/*.py | wc -l
```
Expected: 5

### Step 6: Set up the Claude Code command and skill

Create the `.claude/` directory structure for the `/thumbgen` command:

```bash
mkdir -p .claude/commands .claude/skills/thumbgen
```

Write `.claude/commands/thumbgen.md` from this module's `.claude/commands/thumbgen.md`.
Write `.claude/skills/thumbgen/SKILL.md` from this module's `.claude/skills/thumbgen/SKILL.md`.

[VERIFY]
```bash
ls .claude/commands/thumbgen.md .claude/skills/thumbgen/SKILL.md
```
Both files should exist.

### Step 7: Set up the brand style template

Write `templates/brand-style.md` from this module's `templates/brand-style.md`.

```bash
mkdir -p templates
```

Tell the user: "I've created a brand style template at `templates/brand-style.md`. Right now it has generic defaults. You can customize it anytime — the more specific you are about your brand (colors, typography, background style, person position), the more consistent your thumbnails will be. For now, the defaults work fine to get started."

### Step 8: Set up your photo catalog — THE MOST IMPORTANT STEP

This is where the magic happens. The multi-photo reference system is what makes this generator produce thumbnails that actually look like you.

**Tell the user:**
"Now we need to set up your reference photos. This is the step that makes the biggest difference in quality. I need you to gather 10-30 photos of yourself — the more variety, the better."

```bash
mkdir -p photos
```

**Guide the user through photo selection:**

"Here's what makes great reference photos:
- **Variety of expressions:** smiling, serious, surprised, contemplative, excited
- **Variety of angles:** straight-on, three-quarter left, three-quarter right
- **Variety of outfits:** different shirts/colors help Gemini distinguish YOU from your clothes
- **High quality:** good lighting, clear face, reasonable resolution
- **No sunglasses or masks** — Gemini needs to see your full face

**Where to find photos:**
- Your phone's camera roll (selfies, photos from events)
- Professional headshots if you have them
- Screenshots from your own YouTube videos (high-quality frames)
- Social media profile photos

Drop them into the `photos/` folder. Any format works — PNG, JPG, JPEG, WebP.

Once you've added your photos, tell me and I'll scan them."

**After the user adds photos:**

1. Run the scanner:
```bash
python3 scripts/analyze_photos.py --scan
```

2. **Help the user classify their photos interactively.** Open `photos/catalog.json` and for each photo:
   - Show them the photo (use the Read tool to display it)
   - Ask: "What expression is this? (confident_smile, serious, shocked, contemplative, angry, smirk, excited, neutral)"
   - Ask: "What pose? (neutral, pointing_at, arms_crossed, hand_on_chin, hands_out_shrug, etc.)"
   - Ask: "What angle? (front, three_quarter_left, three_quarter_right, profile)"
   - Ask: "What framing? (headshot, shoulders_up, waist_up)"
   - Set `curated: true` for photos they want to use
   - Rate quality_score (1-5) and identity_score (1-5) — how clear the face is

   **Minimum:** Classify at least 5-8 photos to get started. More is better.
   **Pro tip:** The best approach is to classify the 8-10 best photos now and add more later.

3. **Update the identity description.** Edit `photos/catalog.json` and replace the placeholder `identity_description` with the user's actual appearance:
   - "YOUR NAME — gender, age range. Hair color and style. Facial hair. Key features: anything distinctive."
   - Be specific — this text gets prepended to every generation prompt.

4. Run the optimizer:
```bash
python3 scripts/analyze_photos.py --optimize
```

[VERIFY]
```bash
python3 -c "
import json
with open('photos/catalog.json') as f:
    catalog = json.load(f)
curated = [p for p in catalog['photos'] if p.get('curated')]
print(f'Catalog ready: {len(curated)} curated photos out of {len(catalog[\"photos\"])} total')
if len(curated) < 5:
    print('Warning: You should have at least 5 curated photos for good results')
"
```

Expected: "Catalog ready: X curated photos out of Y total" (X should be 5+)

After photo setup: "Your photo catalog is ready! This is the foundation of the whole system — the more photos you classify, the better your thumbnails will look."

### Step 9: Create output directories

```bash
mkdir -p outputs/thumbnails/examples outputs/thumbnails/refs
```

---

## TEST

Run the module and verify it works end-to-end.

### Quick test — Photo selection

Test that the photo selector works with your catalog:
```bash
cd ~/thumbnail-generator && source .venv/bin/activate
python3 scripts/photo_selector.py --expression confident_smile --count 3
```
Expected: JSON output showing 3 selected photos (1 primary + 2 supporting) with labels and paths.

### Quick test — YouTube search

Test the competitor research script:
```bash
python3 scripts/search_examples.py --query "how to start a business" --top 3
```
Expected: Downloads 3 thumbnail images to `outputs/thumbnails/examples/` and prints a JSON manifest.

### Full test — Generate a thumbnail

Generate a single test thumbnail:
```bash
python3 scripts/photo_selector.py \
    --expression confident_smile \
    --count 4 \
    --output outputs/thumbnails/test/photo-selection.json

python3 scripts/generate_thumbnail.py \
    --photo-selection outputs/thumbnails/test/photo-selection.json \
    --prompt "A professional YouTube thumbnail in 16:9 aspect ratio. Place the person on the right side, shoulders up, with a confident smile. Dark cinematic background. Bold white text saying 'TEST' in the upper left. Professional, high-contrast, clean design." \
    --output outputs/thumbnails/test/test.png
```
Expected: A thumbnail image saved to `outputs/thumbnails/test/test.png`.

Show the user the generated thumbnail using the Read tool.

If test works: "It works! You just generated your first AI thumbnail. Here's what happened: the system selected your best photos for a 'confident smile' expression, sent them to Gemini with your brand style guide, and got back a professional thumbnail with your likeness. Now you can use `/thumbgen` for any video topic and get 4 different concepts instantly."

If test fails:
- **"GOOGLE_API_KEY not set"** → Check `.env` file exists and has the key
- **"Catalog not found"** → Run `python3 scripts/analyze_photos.py --scan` first
- **"No curated photos"** → Open `photos/catalog.json` and set `curated: true` on your photos
- **"No image generated"** → Try simplifying the prompt, or try again (API can intermittently fail)

---

## WHAT'S NEXT

Now that the Thumbnail Generator is running, here are your options:

1. **Try `/thumbgen "your video topic"`** — Open Claude Code in your `~/thumbnail-generator` folder and run the command. It will generate 4 different concepts, show you a comparison grid, and let you iterate.

2. **Customize your brand style** — Edit `templates/brand-style.md` with your actual brand colors, typography preferences, and composition rules. The more specific you are, the more consistent your thumbnails will be across videos.

3. **Add more photos** — The more classified photos you have (aim for 15-20+), the better the face likeness. Drop new photos in `photos/`, run `python3 scripts/analyze_photos.py --scan`, classify them, then run `--optimize`.

4. **Study the psychology** — Read `.claude/skills/thumbgen/SKILL.md` for the full thumbnail strategy framework (desire loops, stun gun elements, composition types). Understanding WHY thumbnails work will help you give better feedback during iteration.

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
