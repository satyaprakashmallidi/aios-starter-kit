#!/usr/bin/env python3
"""
Generate a YouTube thumbnail using Gemini image generation.

Usage:
    With intelligent photo selection (recommended):
    python3 scripts/generate_thumbnail.py \
        --photo-selection outputs/thumbnails/my-video/photo-selection.json \
        --prompt "detailed prompt text" \
        --output outputs/thumbnails/my-video/a.png

    With single headshot (legacy):
    python3 scripts/generate_thumbnail.py \
        --headshot photos/optimized/best.png \
        --prompt "detailed prompt text" \
        --output outputs/thumbnails/my-video/a.png

    With reference images (logos, screenshots for composition):
    python3 scripts/generate_thumbnail.py \
        --photo-selection outputs/thumbnails/my-video/photo-selection.json \
        --reference path/to/logo.png path/to/screenshot.png \
        --prompt "detailed prompt text" \
        --output outputs/thumbnails/my-video/a.png

    With example thumbnails from high-performing videos:
    python3 scripts/generate_thumbnail.py \
        --photo-selection outputs/thumbnails/my-video/photo-selection.json \
        --examples path/to/example1.jpg path/to/example2.jpg \
        --prompt "detailed prompt text" \
        --output outputs/thumbnails/my-video/a.png

    With reference image for iteration:
    python3 scripts/generate_thumbnail.py \
        --photo-selection outputs/thumbnails/my-video/photo-selection.json \
        --reference path/to/previous-thumbnail.png \
        --prompt "edit instruction" \
        --output outputs/thumbnails/my-video/v2.png

Environment:
    GOOGLE_API_KEY must be set in .env (get yours at https://aistudio.google.com/apikey)

Credit: Built on Tyler Germain's (@itstylergermain) thumbnail generator at Friday Labs.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Enable AVIF support — YouTube thumbnails are often served in AVIF format
try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass


def find_project_root():
    """Find the project root by looking for .env or known directories."""
    script_dir = Path(__file__).resolve().parent
    # If we're in scripts/, project root is one level up
    if script_dir.name == "scripts":
        return script_dir.parent
    # Otherwise walk up looking for .env
    current = script_dir
    for _ in range(5):
        if (current / ".env").exists() or (current / "scripts").is_dir():
            return current
        current = current.parent
    return Path.cwd()


PROJECT_ROOT = find_project_root()


def parse_args():
    parser = argparse.ArgumentParser(description="Generate YouTube thumbnail via Gemini")
    photo_group = parser.add_mutually_exclusive_group(required=True)
    photo_group.add_argument(
        "--photo-selection",
        help="Path to photo selection JSON from photo_selector.py (recommended)"
    )
    photo_group.add_argument(
        "--headshot", nargs="+",
        help="Path(s) to headshot reference image(s) (legacy — use --photo-selection instead)"
    )
    parser.add_argument(
        "--reference", nargs="*", default=[],
        help="Path(s) to additional reference images (logos, screenshots, or previous thumbnail for iteration)"
    )
    parser.add_argument(
        "--examples", nargs="*", default=[],
        help="Path(s) to example thumbnails from high-performing videos (style inspiration)"
    )
    parser.add_argument(
        "--prompt", required=True,
        help="Detailed prompt for thumbnail generation"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file path for the generated thumbnail"
    )
    parser.add_argument(
        "--no-style", action="store_true",
        help="Skip appending the brand style guide to the prompt"
    )
    return parser.parse_args()


def validate_image_file(path):
    """Check that a file is actually an image, not HTML or other junk from a failed download."""
    p = Path(path)
    if not p.exists():
        print(
            f"Error: File not found: {path}\n"
            f"Make sure the file path is correct and the file exists.",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(p, "rb") as f:
        header = f.read(256)
    if b"<!DOCTYPE" in header or b"<html" in header or b"<HTML" in header:
        print(
            f"Error: '{path}' is an HTML file, not an image. "
            f"The download URL likely returned a web page instead of the actual image. "
            f"Try downloading from a different source.",
            file=sys.stderr,
        )
        sys.exit(1)
    if len(header) < 8:
        print(
            f"Error: '{path}' is too small to be a valid image ({len(header)} bytes). "
            f"The file may be corrupted or the download may have failed.",
            file=sys.stderr,
        )
        sys.exit(1)


def resize_if_needed(img, max_edge=2048):
    """Resize image if larger than max_edge on any side (saves API bandwidth)."""
    w, h = img.size
    if max(w, h) > max_edge:
        ratio = max_edge / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        return img.resize(new_size, Image.LANCZOS)
    return img


def main():
    args = parse_args()

    # Load environment variables from .env
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "Error: GOOGLE_API_KEY not set.\n"
            "Add it to your .env file: GOOGLE_API_KEY=your_key_here\n"
            "Get yours at: https://aistudio.google.com/apikey",
            file=sys.stderr,
        )
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Build the prompt
    prompt = args.prompt

    # Append brand style guide unless --no-style is set
    if not args.no_style:
        style_path = PROJECT_ROOT / "templates" / "brand-style.md"
        if style_path.exists():
            style_text = style_path.read_text().strip()
            prompt += (
                "\n\nBRAND STYLE GUIDE (follow these rules):\n"
                f"{style_text}"
            )

    # If using example thumbnails, add the style examples instruction
    if args.examples:
        prompt += (
            "\n\nSTYLE EXAMPLES:\n"
            "The final attached images are thumbnails from high-performing YouTube videos "
            "on this topic. Study their composition, color usage, text placement, and visual "
            "hierarchy — then apply those patterns to create an ORIGINAL thumbnail. "
            "Do NOT copy these thumbnails. Use them as inspiration for what works."
        )

    contents = []

    # Build content array based on photo source
    if args.photo_selection:
        # Intelligent photo selection: interleave text labels between images
        selection_path = Path(args.photo_selection)
        if not selection_path.exists():
            print(
                f"Error: Photo selection file not found: {args.photo_selection}\n"
                f"Run photo_selector.py first to create a selection.",
                file=sys.stderr,
            )
            sys.exit(1)

        with open(selection_path) as f:
            selection = json.load(f)

        # Prepend identity description to prompt
        identity = selection.get("identity_description", "")
        if identity:
            prompt = (
                f"PERSON IDENTITY: {identity}\n"
                "The following reference photos show this person from multiple angles. "
                "The PRIMARY photo shows the desired expression/pose. "
                "SUPPORTING photos reinforce identity features — use them to ensure "
                "accurate face likeness, hair texture, and distinctive features.\n\n"
                + prompt
            )

        contents.append(prompt)

        # Interleave labeled text between each photo image
        for i, photo in enumerate(selection["photos"], 1):
            photo_path = Path(photo["path"])
            # Resolve relative paths from project root
            if not photo_path.is_absolute():
                photo_path = PROJECT_ROOT / photo_path
            validate_image_file(photo_path)
            contents.append(f"[Image {i}: {photo['label']}]")
            img = resize_if_needed(Image.open(photo_path))
            contents.append(img)

        print(f"Using {len(selection['photos'])} reference photos (photo selection mode)", file=sys.stderr)
    else:
        # Legacy headshot mode
        contents.append(prompt)
        for headshot_path in args.headshot:
            validate_image_file(headshot_path)
            img = resize_if_needed(Image.open(headshot_path))
            contents.append(img)

    # Add reference images (logos, screenshots, previous thumbnails)
    for ref_path in args.reference:
        validate_image_file(ref_path)
        img = resize_if_needed(Image.open(ref_path))
        contents.append(img)

    # Add example thumbnails (style inspiration from high-performing videos)
    for ex_path in args.examples:
        validate_image_file(ex_path)
        img = resize_if_needed(Image.open(ex_path))
        contents.append(img)

    # Generate the thumbnail via Gemini
    print("Generating thumbnail...", file=sys.stderr)
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
            ),
        ),
    )

    # Process response — extract image and any text notes
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_saved = False
    text_response = ""

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data is not None:
            img = part.as_image()
            img.save(str(output_path))
            image_saved = True
            print(f"Thumbnail saved to: {output_path}")
        elif hasattr(part, "text") and part.text is not None:
            text_response += part.text

    if text_response:
        print(f"\nModel notes: {text_response}")

    if not image_saved:
        print(
            "Error: No image was generated in the response.\n"
            "This can happen if the prompt triggered content filtering. "
            "Try simplifying the prompt or removing potentially flagged content.",
            file=sys.stderr,
        )
        if text_response:
            print(f"Response text: {text_response}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
