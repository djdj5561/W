@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo 未检测到 Python，请先安装 Python 3.10 或更高版本。
  pause
  exit /b 1
)

where ollama >nul 2>&1
if errorlevel 1 (
  echo 未检测到 Ollama，请先安装 Ollama。
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo 正在创建 Python 虚拟环境...
  python -m venv .venv
  if errorlevel 1 (
    echo 虚拟环境创建失败。
    pause
    exit /b 1
  )
)

echo 正在检查 Python 依赖...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo 依赖安装失败，请检查网络后重试。
  pause
  exit /b 1
)

ollama list >nul 2>&1
if errorlevel 1 (
  echo 正在启动 Ollama 服务...
  start "Ollama" /min cmd /c "ollama serve"
  timeout /t 3 /nobreak >nul
)

ollama list | findstr /i "qwen2.5:7b" >nul 2>&1
if errorlevel 1 (
  echo 正在准备 qwen2.5:7b 模型，首次运行需要下载约 4.7 GB...
  ollama pull qwen2.5:7b
  if errorlevel 1 (
    echo 模型下载失败，请检查网络后重新双击本文件。
    pause
    exit /b 1
  )
)

echo 正在启动校园办事指南助手...
start "校园办事指南助手" http://127.0.0.1:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
pause
