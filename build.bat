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
    --name "DAW Project Browser" ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --hidden-import=webview ^
    --hidden-import=webview.platforms.winforms ^
    --hidden-import=flask ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --noconfirm ^
    app.py

echo.
echo Done! Executable is at: dist\DAW Project Browser\DAW Project Browser.exe
pause
