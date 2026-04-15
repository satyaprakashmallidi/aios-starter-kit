# ThumbGen — AI Thumbnail Generation

> Generate professional YouTube thumbnails using the ThumbGen skill.

## Instructions

### 1. Parse the Input

The user provides a video topic or title. Use it directly.

### 2. Load the ThumbGen Skill

Read the skill definition:
```
.claude/skills/thumbgen/SKILL.md
```

Also read the brand style guide:
```
templates/brand-style.md
```

### 3. Run the ThumbGen Workflow

Follow the skill's 6-step process exactly:

1. **Step 1:** Confirm topic, ask about visual assets, select reference photos via `photo_selector.py` (expression-matched per concept)
2. **Step 1b:** Search for high-performing examples via `search_examples.py`
3. **Step 2:** Define desire loop, craft 4 concept prompts
4. **Step 2b:** Gather reference images (logos, screenshots) for concepts
5. **Step 3:** Generate all 4 thumbnails in parallel using `--photo-selection`
6. **Step 4:** Create 2x2 comparison grid
7. **Step 5:** Present to user with descriptions of each concept
8. **Step 6:** Iterate based on feedback

### 4. Output Location

All thumbnails save to:
```
outputs/thumbnails/{video-slug}/
├── a.png, b.png, c.png, d.png    # 4 concepts
├── comparison.png                  # 2x2 grid
├── v2.png, v3.png ...             # Iterations
└── final.png                       # Selected final
```

### 5. Key Rules

- **Follow the skill exactly** — don't skip steps or modify the psychology/strategy framework
- **Brand style matters** — always read templates/brand-style.md before crafting prompts
- **4 genuinely different concepts** — not color swaps, real variation in composition, text, and desire loop angle
- **Complementary text** — thumbnail text must complement the title, never repeat it
- **Interactive** — present concepts before generating, get user approval at each stage

ARGUMENTS: $ARGUMENTS
