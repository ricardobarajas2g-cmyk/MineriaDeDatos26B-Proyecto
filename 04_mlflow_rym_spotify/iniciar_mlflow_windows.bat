@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Primero crea el entorno .venv e instala requirements.txt
  exit /b 1
)
.venv\Scripts\python.exe -m mlflow server --backend-store-uri sqlite:///mlflow.db --artifacts-destination ./mlartifacts --host 127.0.0.1 --port 5000
