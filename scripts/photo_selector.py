#!/usr/bin/env python3
"""
Intelligent photo selector for thumbnail generation.

Selects the optimal set of reference photos for Gemini thumbnail generation
using a Primary + Supporting strategy:
- 1 primary photo matching the desired pose/expression
- N supporting photos for identity reinforcement (diverse angles/attire)

The multi-photo approach with interleaved text labels dramatically improves
face likeness compared to using a single headshot.

Usage:
    python3 scripts/photo_selector.py \
        --expression confident_smile \
        --pose neutral \
        --count 4 \
        --output outputs/thumbnails/my-video/photo-selection.json

    python3 scripts/photo_selector.py \
        --expression shocked \
        --count 3
"""

import argparse
import json
import sys
from pathlib import Path


def find_project_root():
    """Find the project root by looking for known directories."""
    script_dir = Path(__file__).resolve().parent
    if script_dir.name == "scripts":
        return script_dir.parent
    current = script_dir
    for _ in range(5):
        if (current / "photos").is_dir() or (current / "scripts").is_dir():
            return current
        current = current.parent
    return Path.cwd()


PROJECT_ROOT = find_project_root()
CATALOG_PATH = PROJECT_ROOT / "photos" / "catalog.json"

# Expression families for fuzzy matching
# If someone wants "confident_smile" but that exact photo doesn't exist,
# we can fall back to similar expressions
EXPRESSION_FAMILIES = {
    "confident_smile": ["confident_smile", "smirk", "excited"],
    "serious": ["serious", "contemplative", "angry", "neutral"],
    "shocked": ["shocked", "excited"],
    "contemplative": ["contemplative", "serious", "neutral"],
    "angry": ["angry", "serious"],
    "smirk": ["smirk", "confident_smile"],
    "excited": ["excited", "confident_smile", "shocked"],
    "neutral": ["neutral", "contemplative", "serious"],
}

# Emotion-to-expression mapping
# These shortcuts let you say "confidence" instead of "confident_smile"
EMOTION_MAP = {
    "confidence": "confident_smile",
    "shock": "shocked",
    "discovery": "shocked",
    "curiosity": "contemplative",
    "authority": "serious",
    "excitement": "excited",
    "teaching": "confident_smile",
    "warning": "angry",
    "frustration": "angry",
    "skepticism": "contemplative",
}


def load_catalog(catalog_path: Path) -> dict:
    """Load and validate the photo catalog."""
    if not catalog_path.exists():
        print(
            f"Error: Catalog not found at {catalog_path}\n"
            f"Run: python3 scripts/analyze_photos.py --scan\n"
            f"This will scan your photos/ folder and create the catalog.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(catalog_path) as f:
        catalog = json.load(f)

    curated = [p for p in catalog["photos"] if p.get("curated")]
    if not curated:
        print(
            "Error: No curated photos in catalog.\n"
            "Open photos/catalog.json and mark your best photos as curated: true\n"
            "Then classify their expression, pose, angle, etc.\n"
            "You need at least 5-10 curated photos for good results.",
            file=sys.stderr,
        )
        sys.exit(1)

    return catalog


def get_person_name(catalog: dict) -> str:
    """Extract the person's first name from the identity description."""
    identity = catalog.get("identity_description", "")
    if identity:
        # Take the first word (assumed to be the name)
        first_word = identity.split()[0].rstrip(" —-:,")
        if first_word and len(first_word) > 1:
            return first_word
    return "Person"


def score_primary(photo: dict, expression: str, pose: str | None, prop: str | None) -> float:
    """Score a photo for the primary role (best match for desired expression/pose)."""
    score = 0.0

    # Expression match — exact match is best, family match is OK
    if photo["expression"] == expression:
        score += 10
    elif expression in EXPRESSION_FAMILIES and photo["expression"] in EXPRESSION_FAMILIES[expression]:
        score += 3

    # Pose match
    if pose:
        if photo["pose"] == pose:
            score += 5
        elif photo["pose"] in ("neutral", pose):
            score += 2

    # Prop match (laptop, phone, etc.)
    if prop and photo.get("has_prop") == prop:
        score += 8
    elif prop and photo.get("has_prop") is not None:
        score -= 2  # Wrong prop penalty

    # Quality and identity scores from catalog
    score += (photo.get("quality_score") or 0)
    score += (photo.get("identity_score") or 0)

    # Bonus for best_for tag match
    best_for = photo.get("best_for", [])
    if expression in best_for:
        score += 5
    if pose and pose in best_for:
        score += 3

    return score


def score_supporting(photo: dict, primary: dict) -> float:
    """Score a photo for a supporting role (identity reinforcement)."""
    score = 0.0

    # Identity score is paramount for supporting photos
    score += (photo.get("identity_score") or 0) * 2

    # Penalize same expression/pose as primary (want visual diversity)
    if photo["expression"] == primary["expression"]:
        score -= 3
    if photo["pose"] == primary["pose"]:
        score -= 3

    # Reward different angle (helps Gemini understand 3D face structure)
    if photo.get("angle") != primary.get("angle"):
        score += 2

    # Reward different attire (visual diversity)
    if photo.get("attire") != primary.get("attire"):
        score += 1

    # Prefer clean headshots/shoulders for supporting (identity focus)
    if photo.get("framing") in ("headshot", "shoulders_up"):
        score += 1

    # Prefer no props for supporting (cleaner identity signal)
    if photo.get("has_prop") is None:
        score += 1

    # Quality baseline
    score += (photo.get("quality_score") or 0)

    return score


def build_label(photo: dict, role: str, person_name: str) -> str:
    """Build a descriptive text label for interleaving with the image."""
    parts = []
    if photo.get("expression"):
        parts.append(photo["expression"].replace("_", " "))
    if photo.get("angle"):
        parts.append(photo["angle"].replace("_", " ") + " angle")
    if photo.get("attire"):
        parts.append(photo["attire"].replace("_", " "))
    if photo.get("has_prop"):
        parts.append(f"holding {photo['has_prop']}")

    desc = ", ".join(parts)

    if role == "primary":
        return f"PRIMARY: {person_name} {desc}"
    else:
        return f"SUPPORTING: Same person ({person_name}), {desc}"


def select_photos(
    catalog: dict,
    expression: str,
    pose: str | None = None,
    prop: str | None = None,
    count: int = 4,
) -> dict:
    """Select optimal photo set using Primary + Supporting strategy."""
    curated = [p for p in catalog["photos"] if p.get("curated")]
    person_name = get_person_name(catalog)

    # Resolve emotion shortcut to expression if needed
    if expression in EMOTION_MAP:
        expression = EMOTION_MAP[expression]

    # Score all photos for primary role
    primary_scores = []
    for photo in curated:
        score = score_primary(photo, expression, pose, prop)
        primary_scores.append((score, photo))

    primary_scores.sort(key=lambda x: x[0], reverse=True)
    primary = primary_scores[0][1]

    # Score remaining photos for supporting roles
    remaining = [p for p in curated if p["id"] != primary["id"]]
    supporting_scores = []
    for photo in remaining:
        score = score_supporting(photo, primary)
        supporting_scores.append((score, photo))

    supporting_scores.sort(key=lambda x: x[0], reverse=True)
    supporting = [p for _, p in supporting_scores[: count - 1]]

    # Build output with paths relative to project root
    photos = []
    photos.append({
        "path": primary["optimized_path"],
        "role": "primary",
        "label": build_label(primary, "primary", person_name),
        "id": primary["id"],
        "expression": primary["expression"],
    })
    for photo in supporting:
        photos.append({
            "path": photo["optimized_path"],
            "role": "supporting",
            "label": build_label(photo, "supporting", person_name),
            "id": photo["id"],
            "expression": photo["expression"],
        })

    return {
        "photos": photos,
        "identity_description": catalog["identity_description"],
        "selection_params": {
            "expression": expression,
            "pose": pose,
            "prop": prop,
            "count": count,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Intelligent photo selector for thumbnail generation")
    parser.add_argument(
        "--expression", required=True,
        help="Desired expression (confident_smile, serious, shocked, contemplative, angry, smirk, excited, neutral) "
             "or emotion shortcut (confidence, authority, shock, curiosity, excitement, teaching, warning, frustration, skepticism)"
    )
    parser.add_argument(
        "--pose", default=None,
        help="Desired pose (neutral, pointing_at, pointing_up, arms_crossed, hand_on_chin, hands_out_shrug, holding_phone, holding_laptop, gesturing)"
    )
    parser.add_argument(
        "--prop", default=None,
        help="Desired prop in the photo (laptop, phone, notebook)"
    )
    parser.add_argument(
        "--count", type=int, default=4,
        help="Total number of photos to select: 1 primary + N-1 supporting (default: 4)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output JSON path (prints to stdout if omitted)"
    )
    parser.add_argument(
        "--catalog", default=str(CATALOG_PATH),
        help="Path to catalog.json (default: photos/catalog.json)"
    )
    args = parser.parse_args()

    catalog = load_catalog(Path(args.catalog))
    result = select_photos(catalog, args.expression, args.pose, args.prop, args.count)

    output_json = json.dumps(result, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(output_json)
        print(f"Photo selection saved to {args.output}")
    else:
        print(output_json)

    # Print summary to stderr
    print(f"\nSelected {len(result['photos'])} photos:", file=sys.stderr)
    for p in result["photos"]:
        print(f"  [{p['role'].upper()}] {p['id']} — {p['expression']}", file=sys.stderr)


if __name__ == "__main__":
    main()
