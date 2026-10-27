#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null
python3 -c 'import sys; assert sys.version_info >= (3,11)'
mkdir -p work/pip-cache work/font-cache
python3 -m venv --system-site-packages .venv
PIP_CACHE_DIR="$PWD/work/pip-cache" .venv/bin/python -m pip install --disable-pip-version-check -r episodes/01/sources/requirements-render.lock
.venv/bin/python - <<'PY'
import cairosvg, numpy, PIL
assert cairosvg.svg2png(bytestring=b'<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"><circle cx="4" cy="4" r="3"/></svg>').startswith(b'\x89PNG')
print('Python, CairoSVG/Cairo, NumPy et Pillow disponibles.')
PY
