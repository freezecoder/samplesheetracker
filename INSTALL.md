# Installation Guide — Sample Sheet Tracker

---

## Requirements

| Requirement | Minimum version | Notes |
|-------------|----------------|-------|
| Python | 3.10+ | 3.11 or 3.12 recommended |
| pip | 21+ | Comes with Python |
| Git | any | Only needed if cloning from a repository |

> **Note:** Python 3.8/3.9 are not supported. The app uses `str | None` union syntax
> (PEP 604) which requires Python 3.10+.

---

## Option 1 — pip + virtualenv (recommended)

### 1. Get the code

**Clone from a repository:**
```bash
git clone <repo-url>
cd samplesheetracker
```

**Or unzip a downloaded archive:**
```bash
unzip samplesheetracker.zip
cd samplesheetracker
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

| Platform | Command |
|----------|---------|
| macOS / Linux | `source .venv/bin/activate` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |

Your prompt will change to show `(.venv)` when the environment is active.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:

| Package | Purpose |
|---------|---------|
| `streamlit` | Web app framework |
| `pandas` | DataFrame operations |
| `rapidfuzz` | Fuzzy string matching |
| `openpyxl` | Reading Excel files |
| `xlsxwriter` | Writing formatted Excel exports |
| `Pillow` | Image support (logo) |
| `pytest` + `pytest-cov` | Running the test suite |

### 4. Run the app

```bash
streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`.
If it doesn't open, navigate there manually.

### 5. Stop the app

Press `Ctrl+C` in the terminal.

---

## Option 2 — Conda / Miniconda

If you use Conda for environment management:

```bash
conda create -n sampletracker python=3.11
conda activate sampletracker
pip install -r requirements.txt
streamlit run app.py
```

> Use `pip` inside Conda for this project — all packages are on PyPI and the
> `requirements.txt` file is pip-formatted.

---

## Option 3 — No virtual environment (quick test only)

Not recommended for ongoing use, but works for a quick try:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Verifying the Installation

After installing, confirm everything is working:

```bash
# Check Python version (must be 3.10+)
python3 --version

# Check key packages
python3 -c "import streamlit, pandas, rapidfuzz, xlsxwriter; print('OK')"

# Run the test suite (all 69 tests should pass)
pytest tests/ -q
```

Expected test output:
```
.....................................................................    [100%]
69 passed in 0.4s
```

---

## Keeping the App Running

For ongoing lab use, you may want the app to stay running in the background or start automatically.

### Background process (macOS / Linux)

```bash
nohup streamlit run app.py > streamlit.log 2>&1 &
echo $! > streamlit.pid
```

To stop it later:
```bash
kill $(cat streamlit.pid)
```

### Screen / tmux session

```bash
# Using screen
screen -S sampletracker
streamlit run app.py
# Detach: Ctrl+A then D
# Re-attach: screen -r sampletracker

# Using tmux
tmux new -s sampletracker
streamlit run app.py
# Detach: Ctrl+B then D
# Re-attach: tmux attach -t sampletracker
```

### Custom port

If port 8501 is already in use:
```bash
streamlit run app.py --server.port 8502
```

### Network access (share with colleagues on same network)

```bash
streamlit run app.py --server.address 0.0.0.0
```

Colleagues can then access the app at `http://<your-machine-ip>:8501`.

> **Security note:** Only do this on a trusted local network. The app has no authentication.

---

## Updating

Pull the latest code and reinstall dependencies:

```bash
git pull
pip install -r requirements.txt --upgrade
```

Then relaunch:
```bash
streamlit run app.py
```

---

## Troubleshooting

### `python3 --version` shows 3.8 or 3.9

You need Python 3.10+. Install it from [python.org](https://www.python.org/downloads/) or via
your system package manager:

```bash
# macOS with Homebrew
brew install python@3.12

# Ubuntu / Debian
sudo apt install python3.12 python3.12-venv

# Then use python3.12 explicitly
python3.12 -m venv .venv
```

### `ModuleNotFoundError: No module named 'streamlit'`

The virtual environment is not activated, or dependencies were not installed.

```bash
source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### `streamlit: command not found`

Streamlit's executable is inside the virtual environment. Activate it first:

```bash
source .venv/bin/activate
streamlit run app.py
```

Or run via Python directly:

```bash
python3 -m streamlit run app.py
```

### Port 8501 is already in use

Another Streamlit instance is running. Either stop it or use a different port:

```bash
# Find and kill existing instance
pkill -f "streamlit run"

# Or use a different port
streamlit run app.py --server.port 8502
```

### App opens but shows a blank page or import error

Check the terminal output for a Python traceback. The most common cause is a missing package:

```bash
pip install -r requirements.txt
```

### `openpyxl` errors when uploading Excel files

Reinstall openpyxl:
```bash
pip install --upgrade openpyxl
```

### Tests fail after updating

Re-install dependencies to pick up any version changes:

```bash
pip install -r requirements.txt --upgrade
pytest tests/ -q
```

---

## File Permissions (macOS / Linux)

If you downloaded a zip and the script is not executable:

```bash
chmod +x app.py   # not required for streamlit run, but good practice
```

---

## Windows-Specific Notes

- Use **PowerShell** or **Windows Terminal** — the built-in `cmd` works but is less convenient.
- If `python3` is not recognised, try `python` instead (Windows often installs as `python`).
- Virtual environment activation in PowerShell may require:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- File paths use backslashes — the folder path input in the app accepts both `\` and `/`.
