#!/usr/bin/env bash
# Sample Sheet Tracker — quick start script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
PORT="${PORT:-8501}"

# ── 1. Check Python version ───────────────────────────────────────────────────
PYTHON=$(command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3 || true)

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.10+ not found. Install it from https://python.org" >&2
    exit 1
fi

PY_VERSION=$("$PYTHON" -c "import sys; print(sys.version_info.major * 10 + sys.version_info.minor)")
if [ "$PY_VERSION" -lt 310 ]; then
    echo "ERROR: Python 3.10+ required (found $("$PYTHON" --version))" >&2
    exit 1
fi

# ── 2. Create virtual environment if needed ───────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "→ Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# ── 3. Activate ───────────────────────────────────────────────────────────────
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# ── 4. Install / update dependencies ─────────────────────────────────────────
if ! python -c "import streamlit, pandas, rapidfuzz, xlsxwriter" 2>/dev/null; then
    echo "→ Installing dependencies..."
    pip install -r requirements.txt --quiet
fi

# ── 5. Launch ─────────────────────────────────────────────────────────────────
echo "→ Starting Sample Sheet Tracker on port $PORT..."
echo "  Open http://localhost:$PORT in your browser."
echo "  Press Ctrl+C to stop."
echo ""
streamlit run app.py --server.port "$PORT"
