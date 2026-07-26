@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
  echo Virtual environment not found. Running installer first...
  call install.bat
)
call .venv\Scripts\activate.bat
python -m streamlit run aoip\app.py
