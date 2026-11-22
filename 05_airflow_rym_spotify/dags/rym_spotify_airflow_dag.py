"""Práctica 5: Airflow orquesta 5 tareas de RYM + Spotify.
La ejecución de scikit-learn y MLflow ocurre en un worker independiente.
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

WORKER_URL = "http://worker:8000"


def llamar_worker(task: str, force_fail: bool = False):
    """Ejecuta una tarea en el worker y reporta su resultado en los logs."""
    params = urllib.parse.urlencode({"force_fail": str(force_fail).lower()}) if force_fail else ""
    url = f"{WORKER_URL}/tasks/{task}" + (f"?{params}" if params else "")
    request = urllib.request.Request(url, method="POST", data=b"")
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.load(response)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"La tarea '{task}' falló con HTTP {err.code}: {detail}") from err
    print(f"Tarea {task} completada: {json.dumps(result, ensure_ascii=False)}")
    return result


with DAG(
    dag_id="rym_spotify_entrenamiento",
    description="Validación, preparación, entrenamiento, MLflow y reporte de álbumes RYM + Spotify",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,  # Activación manual; cambiar a '@daily' solo para ejercicio
    catchup=False,
    max_active_runs=1,
    tags=["RYM", "Spotify", "MLflow", "MLOps"],
    default_args={"retries": 0, "retry_delay": timedelta(seconds=30)},
) as dag:

    validar = PythonOperator(
        task_id="validar_csv",
        python_callable=llamar_worker,
        op_kwargs={"task": "validate", "force_fail": False},  # cambiar a True para simular fallo
    )
    preparar = PythonOperator(
        task_id="preparar_datos", python_callable=llamar_worker,
        op_kwargs={"task": "prepare"},
    )
    entrenar = PythonOperator(
        task_id="entrenar_modelos", python_callable=llamar_worker,
        op_kwargs={"task": "train"},
    )
    registrar = PythonOperator(
        task_id="registrar_champion", python_callable=llamar_worker,
        op_kwargs={"task": "register"},
    )
    reporte = PythonOperator(
        task_id="generar_reporte", python_callable=llamar_worker,
        op_kwargs={"task": "report"},
    )

    validar >> preparar >> entrenar >> registrar >> reporte
