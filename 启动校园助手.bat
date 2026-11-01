@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo Python was not found. Install Python 3.10 or newer first.
  pause
  exit /b 1
)

where ollama >nul 2>&1
if errorlevel 1 (
  echo Ollama was not found. Install Ollama first.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
)

echo Checking Python dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check the network and try again.
  pause
  exit /b 1
)

ollama list >nul 2>&1
if errorlevel 1 (
  echo Starting Ollama service...
  start "Ollama" /min cmd /c "ollama serve"
  timeout /t 3 /nobreak >nul
)

ollama list | findstr /i "qwen2.5:7b" >nul 2>&1
if errorlevel 1 (
  echo Preparing qwen2.5:7b. The first run downloads about 4.7 GB...
  ollama pull qwen2.5:7b
  if errorlevel 1 (
    echo Model download failed. Check the network and run this file again.
    pause
    exit /b 1
  )
)

echo Starting Campus Guide Assistant...
start "Campus Guide Assistant" http://127.0.0.1:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
pause
