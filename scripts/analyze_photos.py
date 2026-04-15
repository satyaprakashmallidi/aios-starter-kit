#!/usr/bin/env python3
"""
Photo catalog manager for the thumbnail generator.

Two modes:
  --scan      Walk photos/ folder, extract metadata, generate/update catalog.json
  --optimize  Resize all curated photos to 1024px max edge, save to photos/optimized/

The catalog is what powers the intelligent photo selection. You need to:
1. Drop 10-30 photos of yourself into the photos/ folder
2. Run --scan to create catalog.json
3. Edit catalog.json to classify each photo (expression, pose, angle, etc.)
4. Run --optimize to create optimized versions for fast generation

Usage:
    python3 scripts/analyze_photos.py --scan
    python3 scripts/analyze_photos.py --optimize
"""

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image


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
PHOTOS_DIR = PROJECT_ROOT / "photos"
CATALOG_PATH = PHOTOS_DIR / "catalog.json"
OPTIMIZED_DIR = PHOTOS_DIR / "optimized"
MAX_EDGE = 1024


def slugify(filename: str) -> str:
    """Generate a stable slug ID from a filename."""
    name = Path(filename).stem.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    return name


def scan(photos_dir: Path, catalog_path: Path):
    """Walk photos directory, extract metadata, generate catalog.json."""
    image_exts = {".png", ".jpg", ".jpeg", ".webp"}

    if not photos_dir.exists():
        print(
            f"Error: Photos directory not found at {photos_dir}\n"
            f"Create it and add 10-30 photos of yourself:\n"
            f"  mkdir -p {photos_dir}\n"
            f"  # Then copy/paste your photos into that folder",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load existing catalog if present (preserves your classifications on re-scan)
    existing = {}
    if catalog_path.exists():
        with open(catalog_path) as f:
            data = json.load(f)
            for photo in data.get("photos", []):
                existing[photo["filename"]] = photo

    photos = []
    seen_ids = set()

    for p in sorted(photos_dir.iterdir()):
        if p.suffix.lower() not in image_exts:
            continue
        if p.parent.name == "optimized":
            continue

        slug = slugify(p.name)
        # Deduplicate slugs
        if slug in seen_ids:
            counter = 2
            while f"{slug}-{counter}" in seen_ids:
                counter += 1
            slug = f"{slug}-{counter}"
        seen_ids.add(slug)

        # Get image dimensions
        try:
            with Image.open(p) as img:
                width, height = img.size
        except Exception as e:
            print(f"  Warning: Could not open {p.name}: {e}", file=sys.stderr)
            continue

        file_size = p.stat().st_size
        file_size_mb = round(file_size / (1024 * 1024), 1)

        # Preserve existing classifications if available
        prev = existing.get(p.name, {})

        photo = {
            "id": prev.get("id", slug),
            "filename": p.name,
            "original_path": f"photos/{p.name}",
            "optimized_path": f"photos/optimized/{prev.get('id', slug)}.png",
            "width": width,
            "height": height,
            "file_size_mb": file_size_mb,
            "curated": prev.get("curated", False),
            "expression": prev.get("expression", None),
            "pose": prev.get("pose", None),
            "angle": prev.get("angle", None),
            "framing": prev.get("framing", None),
            "lighting": prev.get("lighting", None),
            "attire": prev.get("attire", None),
            "background": prev.get("background", None),
            "has_prop": prev.get("has_prop", None),
            "quality_score": prev.get("quality_score", None),
            "identity_score": prev.get("identity_score", None),
            "best_for": prev.get("best_for", []),
            "notes": prev.get("notes", ""),
        }
        photos.append(photo)

    # Build catalog with placeholder identity description
    existing_identity = ""
    if catalog_path.exists():
        with open(catalog_path) as f:
            existing_identity = json.load(f).get("identity_description", "")

    catalog = {
        "version": 1,
        "identity_description": existing_identity or (
            "YOUR NAME — describe your appearance here. Example: "
            "Male, late 20s, brown curly hair, short beard. "
            "Key features: distinctive hair texture, defined jawline. "
            "This description helps the AI match your likeness accurately."
        ),
        "photos": photos,
    }

    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)

    curated_count = sum(1 for p in photos if p["curated"])
    print(f"Catalog written: {catalog_path}")
    print(f"  Total photos: {len(photos)}")
    print(f"  Curated: {curated_count}")
    print(f"  Unclassified: {len(photos) - curated_count}")

    if curated_count == 0:
        print(
            "\nNext steps:"
            "\n  1. Open photos/catalog.json"
            "\n  2. For each photo you want to use, set \"curated\": true"
            "\n  3. Classify each curated photo with expression, pose, angle, etc."
            "\n  4. Update the identity_description with your actual appearance"
            "\n  5. Run: python3 scripts/analyze_photos.py --optimize"
            "\n"
            "\nExpression options: confident_smile, serious, shocked, contemplative, angry, smirk, excited, neutral"
            "\nPose options: neutral, pointing_at, pointing_up, arms_crossed, hand_on_chin, hands_out_shrug, holding_phone, holding_laptop, gesturing"
            "\nAngle options: front, three_quarter_left, three_quarter_right, profile"
            "\nFraming options: headshot, shoulders_up, waist_up, full_body"
        )


def optimize(catalog_path: Path, optimized_dir: Path):
    """Resize all curated photos to MAX_EDGE max edge, save to optimized/."""
    if not catalog_path.exists():
        print(
            f"Error: Catalog not found at {catalog_path}\n"
            f"Run --scan first: python3 scripts/analyze_photos.py --scan",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(catalog_path) as f:
        catalog = json.load(f)

    optimized_dir.mkdir(parents=True, exist_ok=True)

    curated = [p for p in catalog["photos"] if p["curated"]]
    if not curated:
        print(
            "No curated photos found.\n"
            "Open photos/catalog.json and set \"curated\": true for your best photos first.",
        )
        return

    total_size = 0
    for photo in curated:
        src = PHOTOS_DIR / photo["filename"]
        dst = optimized_dir / f"{photo['id']}.png"

        if not src.exists():
            print(f"  Warning: Source not found: {src}", file=sys.stderr)
            continue

        with Image.open(src) as img:
            w, h = img.size
            if max(w, h) > MAX_EDGE:
                ratio = MAX_EDGE / max(w, h)
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            # Convert RGBA to RGB if alpha channel isn't actually used (saves space)
            if img.mode == "RGBA":
                alpha = img.getchannel("A")
                if alpha.getextrema() == (255, 255):
                    img = img.convert("RGB")
            img.save(str(dst), "PNG", optimize=True)

        file_size = dst.stat().st_size
        total_size += file_size
        size_kb = round(file_size / 1024)
        print(f"  {photo['id']}.png — {img.size[0]}x{img.size[1]} — {size_kb} KB")

    total_mb = round(total_size / (1024 * 1024), 1)
    print(f"\nOptimized {len(curated)} photos to {optimized_dir}")
    print(f"Total size: {total_mb} MB")


def main():
    parser = argparse.ArgumentParser(description="Photo catalog manager for thumbnail generation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scan", action="store_true", help="Scan photos/ folder and generate/update catalog.json")
    group.add_argument("--optimize", action="store_true", help="Resize curated photos to 1024px max edge")
    args = parser.parse_args()

    if args.scan:
        scan(PHOTOS_DIR, CATALOG_PATH)
    elif args.optimize:
        optimize(CATALOG_PATH, OPTIMIZED_DIR)


if __name__ == "__main__":
    main()
