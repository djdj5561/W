@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.10 or newer is required.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating the Python environment...
  python -m venv .venv
)

echo Installing or checking Python packages...
.venv\Scripts\python.exe -m pip install -r requirements.txt

where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama is required for the real-model demo.
  echo Install it from https://ollama.com/download/windows and run this file again.
  pause
  exit /b 1
)

echo Starting Ollama service...
start "Ollama" /min ollama serve
timeout /t 2 /nobreak >nul

ollama list | findstr /i "qwen2.5:7b" >nul
if errorlevel 1 (
  echo Downloading qwen2.5:7b. This is about 4.7 GB.
  ollama pull qwen2.5:7b
)

echo Starting the Campus Guide Assistant...
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
endlocal
