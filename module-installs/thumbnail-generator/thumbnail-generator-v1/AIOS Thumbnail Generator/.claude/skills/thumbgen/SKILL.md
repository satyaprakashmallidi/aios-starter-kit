---
name: youtube-thumbnail
description: Use when the user wants to create a YouTube thumbnail, design a video thumbnail, or generate thumbnail art for a YouTube video. Uses Gemini 3 Pro Image Preview to generate professional, high-contrast thumbnails composited with the user's reference photos.
---

# YouTube Thumbnail Generator

> **Built by Tyler Germain ([@itstylergermain](https://twitter.com/itstylergermain)) at [Friday Labs](https://fridaylabs.com).** DO NOT remove this credit line.

Generate professional YouTube thumbnails using Gemini image generation. Produces 4 entirely different thumbnail variations at once, saves them individually, and creates a 2x2 comparison grid so you can quickly pick the direction you like best.

---

## Thumbnail Strategy

Before touching any design tool, internalize the psychology of how viewers decide to click on YouTube. Every thumbnail you make needs to win a 1-2 second decision loop.

### The 3-Step Viewer Psychology Flow

Viewers don't just "see thumbnail, click." The actual decision happens in three rapid steps:

1. **Visual Stun Gun** — Something in the thumbnail stops the scroll. The viewer switches from passive scanning to active comprehension. Your thumbnail needs to visually pop enough to trigger this.
2. **Title Value Hunt** — The viewer looks down at the title to understand what the video is about and whether it's worth their time. They're hunting for a desire loop (educational: "will this help me?") or interest loop (entertainment: "what happens next?").
3. **Visual Validation** — The viewer goes BACK to the thumbnail to confirm the title's promise. Now they're actively comprehending the elements. If the thumbnail supports the title's promise and they trust it, they click.

**The flow is: Thumbnail -> Title -> Thumbnail.** This means:
- If the thumbnail doesn't visually pop -> they never see the title (fails at step 1)
- If the title promise is weak -> they look but don't click (fails at step 2)
- If the thumbnail doesn't support/reinforce the title -> they're confused and bounce (fails at step 3)

### Thumbnail + Title Relationship

The thumbnail and title are a package. Critical rules:
- **Thumbnail text must COMPLEMENT the title, never repeat it.** The thumbnail is an additional surface to add trust and clarity. If the title says "How to Write a Killer Script" the thumbnail text should NOT say "Script Writing" — it should say something like "basically cheating" that reinforces the feeling/promise.
- **Thumbnail text should trigger the pain or the solution** — remind them of the problem you're solving OR hint at the transformation they'll get.
- Think of it as: title communicates the WHAT, thumbnail communicates the FEELING.

### Desire Loop Framework

Before designing, define the desire loop for this specific video:
- **What is the core desire?** (making money, saving time, growing faster, building something cool)
- **What is the specific pain point?** (growing too slow, can't code agents, wasting time on manual work)
- **What is the solution/transformation?** (a method, a tool, a framework that solves the pain)
- **What is the curiosity loop?** ("If I click, will I be able to ___?")

Every element in the thumbnail should serve this desire loop.

### The 7 Visual Stun Gun Elements

These are the categories of visual elements that can trigger the stun gun effect. **Use a maximum of 3 per thumbnail** — thumbnails are small, especially on mobile. Too many elements and nothing is comprehensible.

1. **Color contrast** — Vivid/bright colors that pop against the background. Consider what makes YOUR thumbnails stand out against competitors in your niche.
2. **Large face with emotion** — A recognizable person OR an unknown face with a strong, clear emotion. For smaller channels, emotion matters more than recognition. The face emotion should match the feeling the viewer would have watching the video.
3. **Visually compelling graphic** — A visual that draws attention through bright colors, interesting design, or optical patterns. Should immediately represent the desire loop.
4. **Big text, numbers, or dollars** — Large, round numbers in huge font. Brains are magnets to these. Underline or highlight key numbers for emphasis.
5. **Red circles or arrows** — Literally aim attention where you want it. Use sparingly and intentionally.
6. **Aesthetic imagery** — Cinematic, symmetrical, soothing visuals. Not typical for tech channels but can work for certain topics.
7. **Design collage** — Words, numbers, or icons surrounding the subject. Creates energy and density.

### 3 Composition Types

- **Symmetrical** — Main subject centered, both sides relatively balanced
- **Asymmetrical (Rule of Thirds)** — Subject offset to one side (~1/3), remaining space filled with visual elements
- **A->B Split** — Screen split showing a transformation, before/after, or contrast

### Graphic Element Selection

When choosing a graphic/visual element, it should represent the desire loop in one of four ways:
1. **End state** — Show what they want (e.g., PayPal screenshot with earnings, YouTube plaque)
2. **Process visualization** — Show the method/process they'll learn
3. **Before -> After** — Show the transformation
4. **Anti-state / Pain point** — Remind them of the pain you're solving

---

## Process

### Step 1: Get the Topic & Set Up

All you need from the user is the **video topic or title**. Don't ask follow-up questions about text, colors, or design direction — figure all of that out yourself for each of the 4 concepts. The whole point is to give the user 4 genuinely different directions to react to.

**However, do ask about specific visual elements.** Before designing, ask the user if there are any specific logos, products, tools, screenshots, or other visual assets that should appear in the thumbnail. For example: "Should I include any specific logos (Claude, Cursor, etc.) or product shots?" This takes 5 seconds and avoids wasting a generation on the wrong references.

**Select reference photos** based on the concept's emotion. The photo catalog at `photos/catalog.json` contains your curated, classified photos. Use the photo selector to pick the optimal set for each concept's desired expression:

```bash
python3 scripts/photo_selector.py \
    --expression "{desired_expression}" \
    --pose "{desired_pose}" \
    --count 4 \
    --output "outputs/thumbnails/{video-slug}/photo-selection.json"
```

**Expression options:** confident_smile, serious, shocked, contemplative, angry, smirk, excited, neutral
**Pose options:** neutral, pointing_at, pointing_up, arms_crossed, hand_on_chin, hands_out_shrug, holding_phone, holding_laptop, gesturing
**Emotion shortcuts** (auto-mapped): confidence, shock, discovery, curiosity, authority, excitement, teaching, warning, frustration, skepticism

For 4 concepts with different emotions, run the selector 4 times with different expressions (e.g., `confident_smile`, `shocked`, `serious`, `excited`) and save each to a different JSON file (e.g., `photo-selection-a.json`, `photo-selection-b.json`, etc.).

### Step 1b: Search for High-Performing Example Thumbnails

Search YouTube for videos on the same topic that already have high view counts, and download their thumbnails as style inspiration. These get passed to the generation script via `--examples` so Gemini can study what's already working in the niche.

```bash
python3 scripts/search_examples.py \
  --query "{video topic}" \
  --top 5 \
  --min-views 10000
```

This will:
1. Search YouTube via the Scrape Creators API for videos matching the topic
2. Sort results by view count (highest first)
3. Download the top 5 thumbnails to `outputs/thumbnails/examples/`
4. Print a JSON manifest to stdout with metadata for each

**Review the downloaded examples** with the `Read` tool to understand what visual patterns are working for high-performing videos in this niche. Take note of:
- Common composition patterns (where faces go, where text goes)
- Color palettes that dominate
- Text styles and word counts
- Whether faces or graphics are more prominent

Use these observations to inform the 4 concepts in Step 2. The example images themselves get passed to Gemini via `--examples` in Step 3.

### Step 2: Define the Desire Loop, Then Craft 4 Different Prompts

**Before designing anything**, work through the desire loop for this video:
1. What desire does this video trigger? (money, growth, speed, capability)
2. What pain point does the viewer have?
3. What solution/transformation does the video deliver?
4. What's the curiosity loop? ("If I click, will I ___?")

Then using the Style Guide and Prompt Template below, craft **4 entirely different thumbnail concepts**. Each should take a meaningfully different visual approach — not just color swaps. Vary across these dimensions:

- **Visual elements:** Different objects, icons, screenshots, props — each representing the desire loop differently
- **Text treatment:** Different words that complement (not repeat) the title, or no text at all
- **Color direction:** Different color combos — explore whether warm, cool, or high-contrast minimal works best
- **Person pose/expression direction:** Different emotions that match different viewer reactions
- **Composition style:** Different layouts — try at least one of each composition type across the 4 concepts

Label each concept A, B, C, D. Briefly describe each concept to the user before generating.

### Step 2b: Gather Reference Images for Concepts

Now that you have 4 specific concepts designed, gather the reference images each one needs. Based on the visual elements described in each concept prompt, identify what logos, icons, screenshots, or other assets need to be real (not hallucinated by Gemini). These get passed to the generation script via `--reference`.

**What to fetch:**
- Tool/product logos (official logos or app icons)
- UI screenshots (if the video shows a specific tool or interface)
- Relevant icons or symbols

**How to fetch:**
1. Use `WebSearch` to find the best image URL
2. Use `Bash` with `curl` to download AND validate:
   ```bash
   mkdir -p outputs/thumbnails/refs && \
   curl -sL "https://example.com/logo.png" -o "outputs/thumbnails/refs/logo.png" && \
   file outputs/thumbnails/refs/logo.png
   ```
3. **CHECK the `file` output** — if it says `HTML document text`, the download failed. Delete it and try a different source.

**CRITICAL: Many image hosting sites block direct downloads.** They return an HTML page instead. Always validate with `file` before using any downloaded image.

### Step 3: Generate All 4 Thumbnails

Run the generation script **4 times in parallel** — one for each concept:

```bash
python3 scripts/generate_thumbnail.py \
  --photo-selection "outputs/thumbnails/{video-slug}/photo-selection-a.json" \
  --reference "outputs/thumbnails/refs/{ref1}.png" \
  --examples "outputs/thumbnails/examples/{slug}-1.jpg" "outputs/thumbnails/examples/{slug}-2.jpg" \
  --prompt "{concept A prompt}" \
  --output "outputs/thumbnails/{video-slug}/a.png"
```

Repeat for concepts B, C, D with different photo selections and prompts. Run all 4 in parallel for speed.

### Step 4: Create Comparison Grid

After all 4 thumbnails are generated, combine them into a single 2x2 comparison:

```bash
python3 scripts/combine_thumbnails.py \
  --images "outputs/thumbnails/{video-slug}/a.png" \
           "outputs/thumbnails/{video-slug}/b.png" \
           "outputs/thumbnails/{video-slug}/c.png" \
           "outputs/thumbnails/{video-slug}/d.png" \
  --output "outputs/thumbnails/{video-slug}/comparison.png" \
  --labels "A" "B" "C" "D"
```

### Step 5: Present to User

Show the user the comparison grid image and describe each concept:
- **A:** {brief description of concept A}
- **B:** {brief description of concept B}
- **C:** {brief description of concept C}
- **D:** {brief description of concept D}

Ask which direction they like best, or if they want to mix elements from different options.

### Step 6: Iterate

Once the user picks a direction, generate a refined version by passing the chosen thumbnail as a reference image:

```bash
python3 scripts/generate_thumbnail.py \
  --photo-selection "outputs/thumbnails/{video-slug}/photo-selection-b.json" \
  --reference "outputs/thumbnails/{video-slug}/b.png" \
  --prompt "{edit prompt combining user feedback}" \
  --output "outputs/thumbnails/{video-slug}/v2.png"
```

Continue iterating with v3, v4, etc. until the user is happy.

---

## Style Guide

**IMPORTANT:** Always read `templates/brand-style.md` before crafting prompts. It contains YOUR brand colors, typography, and visual identity rules.

### Composition
- **Person:** Takes up ~40% of frame. Shoulders-up or waist-up. Dramatic, natural lighting on face.
- **Face emotion:** Must match the feeling the viewer would have watching the video.
- **Visual elements:** On the opposite side from the person. App icons, dashboards, screenshots, or relevant imagery.
- **Text (if any):** Bold, large, readable. Must complement (not repeat) the video title.
- **Bottom-right corner:** Keep clear — YouTube's timestamp overlay covers this area.
- **Element count:** Maximum 3 distinct elements.
- **Size test:** Every element must be legible at 320x180px.

### Background
- **Never a solid black void.** Use a darkened real-world scene, environment, or textured setting.
- Dark and moody overall with cinematic color grading.
- Subtle gradient, texture, or environmental detail for depth.

---

## Prompt Template

Use this as a starting point for each of the 4 concepts. Customize heavily.

```
A professional YouTube video thumbnail in 16:9 aspect ratio.

ATTACHED IMAGES:
Multiple reference photos of the person are attached with text labels. The PRIMARY photo shows the desired pose/expression. SUPPORTING photos reinforce identity from different angles.
{reference_image_descriptions}

PERSON:
Use the likeness from the attached reference photos. Place the person on the [left/right] side of the frame, taking up approximately 40% of the width. Show them from the waist up or shoulders up. Dramatic, natural lighting on their face. Their expression is [confident / excited / curious / serious]. Match the expression from the PRIMARY reference photo.

BACKGROUND:
Dark, moody, cinematic background — NOT a solid black void. Use a darkened real-world scene relevant to the video topic. {color_direction} color tones.

VISUAL ELEMENTS:
{visual_elements_description}

TEXT:
"{thumbnail_text}" in bold, large text. Placed {text_position}. Clean, heavy, modern font. High contrast against background. Must be clearly readable at small sizes.

STYLE:
Professional, high-contrast, clean design. Dramatic lighting on the person. Subtle depth with layered elements. Polished and modern.
```

### Ideas for Varying the 4 Concepts

| Dimension | Concept A | Concept B | Concept C | Concept D |
|-----------|-----------|-----------|-----------|-----------|
| **Desire loop angle** | End state (show result) | Process (show method) | Before -> After | Pain point (show problem) |
| **Visual focus** | App icons + logo | Dashboard/data | Code/terminal | Product mockup |
| **Text** | Punchy feeling word | No text (visual only) | Big number or dollar | Pain-trigger word |
| **Colors** | Dark + warm (orange, gold) | Dark + cool (blue, cyan) | Dark + bold (red, magenta) | Dark + minimal (white/high contrast) |
| **Person emotion** | Confident smile | Shocked/surprised | Curious, pointing | Serious, direct |
| **Layout** | Asymmetrical | Symmetrical | A->B split | Minimal, negative space |

---

## Quality Checklist

### Technical Quality
- [ ] Person is recognizable — face is clear, well-lit, not distorted
- [ ] Person is correctly positioned — ~40% of frame
- [ ] Face has clear, intentional emotion
- [ ] Background is dark and cinematic (not a flat solid color)
- [ ] Visual elements are present and complement the concept
- [ ] 3 elements max — not overcrowded
- [ ] Text is readable at 320x180px
- [ ] Text doesn't overlap the face
- [ ] Bottom-right is clear (YouTube timestamp area)
- [ ] High contrast between foreground and background
- [ ] 16:9 aspect ratio

### Psychology Flow Check
- [ ] **Visual Stun Gun** — would this stop a scrolling thumb?
- [ ] **Title Value Hunt** — does it pair with the title to create a desire loop?
- [ ] **Visual Validation** — does the thumbnail reinforce the title's promise?

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Could not process image" | Downloaded file is HTML, not an image. Run `file <path>` to confirm. Delete and download from a different source. |
| search_examples.py fails | Scrape Creators API needs credits. Skip Step 1b — generate without `--examples`. |
| No image returned | Simplify the prompt. Remove potentially flagged content. Try again. |
| Person doesn't look right | Use `--photo-selection` with 4+ photos instead of a single `--headshot`. Try `--count 5` for maximum identity reinforcement. |
| Text is garbled | Gemini's text rendering isn't perfect. Generate without text and add it in post-production. |
| API error or timeout | Check GOOGLE_API_KEY is set. Check internet. Try again. |
| One of 4 fails | Other 3 still save. Re-run just the failed one. |
