@echo off
cd /d "%~dp0"
docker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated
pause
