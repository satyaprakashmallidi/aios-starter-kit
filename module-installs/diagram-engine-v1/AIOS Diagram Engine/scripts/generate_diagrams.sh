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
