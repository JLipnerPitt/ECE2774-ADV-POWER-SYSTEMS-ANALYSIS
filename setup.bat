@echo off
REM ──────────────────────────────────────────────────────────────
REM 1) Create venv if it doesn’t exist
IF NOT EXIST ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
) ELSE (
    echo Virtual environment already exists.
)

REM ──────────────────────────────────────────────────────────────
REM 2) Activate venv
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM ──────────────────────────────────────────────────────────────
REM 3) Upgrade pip & install requirements
echo Upgrading pip...
pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

REM ──────────────────────────────────────────────────────────────
echo.
echo [OK] Setup complete! Your venv is ready.
pause