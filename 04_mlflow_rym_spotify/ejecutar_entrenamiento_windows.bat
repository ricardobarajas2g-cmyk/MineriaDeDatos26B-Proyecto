@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Primero crea el entorno .venv e instala requirements.txt
  exit /b 1
)
.venv\Scripts\python.exe -m src.train
