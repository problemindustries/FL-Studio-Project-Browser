@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q -r requirements.txt

echo Building app...
pyinstaller ^
    --windowed ^
    --name "DAW Companion" ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --hidden-import=webview ^
    --hidden-import=webview.platforms.winforms ^
    --noconfirm ^
    app.py

echo.
echo Done! Executable is at: dist\DAW Companion\DAW Companion.exe
pause
