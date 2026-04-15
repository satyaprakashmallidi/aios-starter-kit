#!/usr/bin/env python3
"""
Search YouTube for high-performing videos on a topic and download their thumbnails
as style examples for thumbnail generation.

Studying what already works in your niche dramatically improves thumbnail quality.
The downloaded thumbnails are passed to Gemini via --examples so it can study
the composition, color usage, text placement, and visual hierarchy of proven thumbnails.

Usage:
    python3 scripts/search_examples.py --query "claude code tutorial" --top 5
    python3 scripts/search_examples.py --query "AI agents" --top 3 --min-views 50000

Environment:
    SCRAPECREATORS_API_KEY must be set in .env (get yours at https://scrapecreators.com)

Output:
    Downloads thumbnails to outputs/thumbnails/examples/ and prints a JSON manifest
    to stdout with metadata about each downloaded thumbnail.

Credit: Built on Tyler Germain's (@itstylergermain) thumbnail generator at Friday Labs.
"""

import argparse
import io
import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

# Enable AVIF support — YouTube serves thumbnails in AVIF format
try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass


def find_project_root():
    """Find the project root by looking for known directories."""
    script_dir = Path(__file__).resolve().parent
    if script_dir.name == "scripts":
        return script_dir.parent
    current = script_dir
    for _ in range(5):
        if (current / ".env").exists() or (current / "scripts").is_dir():
            return current
        current = current.parent
    return Path.cwd()


PROJECT_ROOT = find_project_root()


def search_youtube(query, api_key):
    """Search YouTube via the Scrape Creators API."""
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.scrapecreators.com/v1/youtube/search?query={encoded_query}&includeExtras=true"

    req = urllib.request.Request(url, headers={"x-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(
            f"Error: Scrape Creators API returned {e.code}: {body}\n"
            f"Check your SCRAPECREATORS_API_KEY in .env and ensure you have API credits.\n"
            f"Get your key at: https://scrapecreators.com",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def get_best_thumbnail_url(thumbnail_data):
    """Extract the highest-resolution thumbnail URL from the API response."""
    if isinstance(thumbnail_data, str):
        return thumbnail_data
    if isinstance(thumbnail_data, list):
        best = max(thumbnail_data, key=lambda t: t.get("width", 0) * t.get("height", 0), default=None)
        if best:
            return best.get("url", "")
    if isinstance(thumbnail_data, dict):
        return thumbnail_data.get("url", "")
    return ""


def download_thumbnail(url, output_path):
    """Download a thumbnail image, validate it, and convert to JPEG."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()

        # Validate — some sites return HTML instead of images
        if b"<!DOCTYPE" in data[:256] or b"<html" in data[:256]:
            print(f"  Warning: Got HTML instead of image from {url}", file=sys.stderr)
            return False

        if len(data) < 100:
            print(f"  Warning: File too small ({len(data)} bytes) from {url}", file=sys.stderr)
            return False

        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "JPEG", quality=90)
        return True

    except Exception as e:
        print(f"  Warning: Failed to download {url}: {e}", file=sys.stderr)
        return False


def slugify(text, max_len=40):
    """Convert text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:max_len]


def main():
    parser = argparse.ArgumentParser(description="Search YouTube for high-performing thumbnail examples")
    parser.add_argument("--query", required=True, help="Search query (video topic)")
    parser.add_argument("--top", type=int, default=5, help="Number of top thumbnails to download (default: 5)")
    parser.add_argument("--min-views", type=int, default=0, help="Minimum view count filter (default: 0)")
    parser.add_argument("--output-dir", default="outputs/thumbnails/examples", help="Output directory")
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not api_key:
        print(
            "Error: SCRAPECREATORS_API_KEY not set.\n"
            "Add it to your .env file: SCRAPECREATORS_API_KEY=your_key_here\n"
            "Get yours at: https://scrapecreators.com",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Searching YouTube for: {args.query}", file=sys.stderr)
    data = search_youtube(args.query, api_key)

    videos = data.get("videos", [])
    if not videos:
        print("No videos found for this query.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(videos)} videos", file=sys.stderr)

    # Parse view counts and filter
    for v in videos:
        v["_views"] = v.get("viewCountInt", 0) or 0
    videos = [v for v in videos if v["_views"] >= args.min_views]
    videos.sort(key=lambda v: v["_views"], reverse=True)

    if not videos:
        print(f"No videos found with >= {args.min_views} views.", file=sys.stderr)
        sys.exit(1)

    top_videos = videos[:args.top]

    print(f"\nTop {len(top_videos)} videos by views:", file=sys.stderr)
    for i, v in enumerate(top_videos):
        print(f"  {i+1}. [{v['_views']:,} views] {v.get('title', 'Untitled')}", file=sys.stderr)

    # Download thumbnails
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    query_slug = slugify(args.query)

    manifest = []
    for i, v in enumerate(top_videos):
        thumb_url = get_best_thumbnail_url(v.get("thumbnail", ""))
        if not thumb_url:
            print(f"  Skipping video {i+1}: no thumbnail URL", file=sys.stderr)
            continue

        filename = f"{query_slug}-{i+1}.jpg"
        output_path = output_dir / filename

        print(f"  Downloading thumbnail {i+1}: {v.get('title', '')[:60]}...", file=sys.stderr)
        if download_thumbnail(thumb_url, output_path):
            manifest.append({
                "path": str(output_path),
                "title": v.get("title", ""),
                "views": v["_views"],
                "channel": v.get("channel", {}).get("title", ""),
                "url": v.get("url", ""),
            })

    if not manifest:
        print(
            "Error: Failed to download any thumbnails.\n"
            "This can happen if YouTube thumbnail URLs have changed.\n"
            "Try a different search query.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nDownloaded {len(manifest)} thumbnails to {output_dir}/", file=sys.stderr)

    # Print manifest to stdout (machine-readable for the /thumbgen command to parse)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
