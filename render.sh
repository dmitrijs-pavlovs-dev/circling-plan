#!/usr/bin/env bash
# Render cover / social HTML templates to PNG with headless Chrome.
#
#   ./render.sh                 # re-render every cover into brand/out/
#   ./render.sh 24 25           # only covers 24 and 25
#   ./render.sh social          # only the Instagram formats
#
# Each template declares its own pixel size, so the window size is looked up
# per format rather than passed in.

set -euo pipefail
cd "$(dirname "$0")"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME"; exit 1; }

mkdir -p brand/out

shot() { # shot <html-path> <out-path> <w> <h>
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --window-size="$3,$4" --virtual-time-budget=12000 \
    --screenshot="$2" "file://$PWD/$1" 2>/dev/null
  echo "  → $2"
}

render_social() {
  shot brand/social/ig-square.html brand/out/ig-square.png 1080 1080
  shot brand/social/ig-story.html  brand/out/ig-story.png  1080 1920
}

render_ads() {
  for f in brand/social/ad-*.html; do
    n="${f##*/}"; n="${n%.html}"
    shot "$f" "brand/out/$n.png" 1080 1080
  done
  for f in brand/covers/ad-wide-*.html; do
    n="${f##*/}"; n="${n%.html}"
    shot "$f" "brand/out/$n.png" 1920 1005
  done
  for f in brand/social/story-*.html; do
    n="${f##*/}"; n="${n%.html}"
    shot "$f" "brand/out/$n.png" 1080 1920
  done
}

if [ "${1:-}" = "social" ]; then
  render_social
  exit 0
fi

if [ "${1:-}" = "ads" ]; then
  render_ads
  exit 0
fi

if [ $# -gt 0 ]; then
  targets=("$@")
else
  targets=()
  for f in brand/covers/cover-*.html; do
    n="${f##*cover-}"; targets+=("${n%.html}")
  done
fi

for n in "${targets[@]}"; do
  shot "brand/covers/cover-$n.html" "brand/out/cover-$n.png" 1920 1005
done

[ $# -eq 0 ] && render_social || true
