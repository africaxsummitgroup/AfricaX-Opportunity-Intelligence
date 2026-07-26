@echo off
setlocal
cd /d "%~dp0"
echo Installing AOIP dependencies...
if not exist ".tmp" mkdir ".tmp"
set TMP=%CD%\.tmp
set TEMP=%CD%\.tmp
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Installation complete. Double-click launch.bat to start AOIP.
pause
