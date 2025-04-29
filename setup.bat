@echo off
REM switch to UTF-8 if you’re using any non-ASCII chars
chcp 65001 >nul

REM 0) make sure we’re in the project root
cd /d %~dp0

REM 1) Create venv if it doesn’t exist
IF NOT EXIST ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
) ELSE (
    echo Virtual environment already exists.
)

REM 2) Activate venv
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM ── UPGRADE PIP ─────────────────────────────────────────────────────
echo Upgrading pip (if needed)…
python -m pip install --upgrade pip

REM ── INSTALL REQUIREMENTS ────────────────────────────────────────────
echo Installing dependencies…
pip install -r requirements.txt

echo.
echo [OK] Setup complete!
pause