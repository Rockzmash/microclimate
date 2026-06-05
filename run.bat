@echo off
echo.
echo   🔮  M I C R O C L I M A T E
echo   ─────────────────────────
echo.
echo   Starting proxy server...
echo.

cd /d "%~dp0proxy"

REM Create venv if needed, install deps
if not exist ".venv" (
    echo   Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo   Proxy running at http://localhost:8765
echo.
echo   Open that URL in your browser (Firefox recommended).
echo   Press Ctrl+C here to shut everything down.
echo   ─────────────────────────────────────────
echo.

python server.py
pause
