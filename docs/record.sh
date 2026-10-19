#!/bin/sh
# Regenerates docs/demo.gif. Needs asciinema and agg.
# agg stalls when it writes to the external drive this repo lives on, so it renders to a temp dir first.
cd "$(dirname "$0")/.." || exit 1
asciinema rec --overwrite --idle-time-limit 2 --window-size 84x18 -c ".venv/bin/python docs/demo.py" docs/demo.cast
tmp=$(mktemp -d)
agg --theme github-light --font-family Menlo --font-size 18 --idle-time-limit 2 docs/demo.cast "$tmp/demo.gif" && mv "$tmp/demo.gif" docs/demo.gif
rmdir "$tmp"
