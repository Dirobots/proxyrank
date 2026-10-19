#!/bin/sh
# Regenerates docs/demo.gif. Needs asciinema and agg.
cd "$(dirname "$0")/.." || exit 1
asciinema rec --overwrite --idle-time-limit 2 --window-size 84x18 -c ".venv/bin/python docs/demo.py" docs/demo.cast
agg --theme github-light --font-size 18 --idle-time-limit 2 docs/demo.cast docs/demo.gif
