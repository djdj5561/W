@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1 || (echo Python not found. Install Python 3.10+ first.& pause & exit /b 1)
where ollama >nul 2>&1 || (echo Ollama not found. Install Ollama first.& pause & exit /b 1)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv || (echo Failed to create virtual environment.& pause & exit /b 1)
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt || (echo Dependency installation failed.& pause & exit /b 1)

ollama list | findstr /i "qwen2.5:7b" >nul 2>&1
if errorlevel 1 (
  echo Downloading qwen2.5:7b model. This may take a while...
  ollama pull qwen2.5:7b || (echo Model download failed.& pause & exit /b 1)
)

echo Opening the application...
start "Campus Guide Assistant" http://127.0.0.1:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
pause
