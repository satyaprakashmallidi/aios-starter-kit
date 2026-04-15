#!/usr/bin/env python3
"""
Combine multiple thumbnail images into a 2x2 comparison grid.

After generating 4 thumbnail concepts, this creates a single side-by-side
image so you can quickly compare and pick the best direction.

Usage:
    python3 scripts/combine_thumbnails.py \
        --images thumb1.png thumb2.png thumb3.png thumb4.png \
        --output comparison.png \
        --labels "A" "B" "C" "D"

Credit: Built on Tyler Germain's (@itstylergermain) thumbnail generator at Friday Labs.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args():
    parser = argparse.ArgumentParser(description="Combine thumbnails into a 2x2 comparison grid")
    parser.add_argument(
        "--images", required=True, nargs="+",
        help="Paths to thumbnail images (expects 4 for a 2x2 grid)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file path for the combined grid image"
    )
    parser.add_argument(
        "--labels", nargs="*", default=["A", "B", "C", "D"],
        help="Labels for each thumbnail (default: A B C D)"
    )
    return parser.parse_args()


def find_font(size):
    """Find a suitable font, trying common system paths across platforms."""
    font_paths = [
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def add_label(img, label):
    """Add a label badge to the top-left corner of an image."""
    draw = ImageDraw.Draw(img)
    font_size = max(28, img.width // 20)
    font = find_font(font_size)

    padding = 12
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    badge_w = text_w + padding * 2
    badge_h = text_h + padding * 2
    margin = 16

    # Semi-transparent dark background badge
    draw.rounded_rectangle(
        [margin, margin, margin + badge_w, margin + badge_h],
        radius=8,
        fill=(0, 0, 0, 200),
    )
    draw.text(
        (margin + padding, margin + padding - bbox[1]),
        label, fill="white", font=font,
    )
    return img


def main():
    args = parse_args()

    images = []
    for path in args.images:
        if not Path(path).exists():
            print(
                f"Error: Image not found: {path}\n"
                f"Make sure all 4 thumbnails were generated successfully.",
                file=sys.stderr,
            )
            sys.exit(1)
        images.append(Image.open(path).convert("RGBA"))

    if len(images) != 4:
        print(f"Warning: Expected 4 images, got {len(images)}. Grid may look uneven.", file=sys.stderr)

    # Normalize all images to the same size (use the first image's dimensions)
    target_w, target_h = images[0].size
    resized = []
    for img in images:
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.LANCZOS)
        resized.append(img)

    # Add labels (A, B, C, D)
    labels = args.labels[:len(resized)]
    for i, (img, label) in enumerate(zip(resized, labels)):
        resized[i] = add_label(img, label)

    # Build 2x2 grid with gap between thumbnails
    gap = 8
    grid_w = target_w * 2 + gap
    grid_h = target_h * 2 + gap
    grid = Image.new("RGBA", (grid_w, grid_h), (20, 20, 20, 255))

    positions = [
        (0, 0),                    # Top-left (A)
        (target_w + gap, 0),       # Top-right (B)
        (0, target_h + gap),       # Bottom-left (C)
        (target_w + gap, target_h + gap),  # Bottom-right (D)
    ]

    for img, pos in zip(resized, positions):
        grid.paste(img, pos)

    # Save the comparison grid
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grid.convert("RGB").save(str(output_path), quality=95)
    print(f"Comparison grid saved to: {output_path}")


if __name__ == "__main__":
    main()
