# Guía del alumno — Práctica 5 (120 minutos)

## Objetivo

Automatizar con un DAG la preparación, comparación de tres clasificadores (Logística, Random Forest, SVM), registro de experimentos MLflow y selección del Champion, empleando el dataset RYM + Spotify.

## Actividades

| Minutos | Actividad | Evidencia |
|---|---|---|
| 0–15 | Identificar componentes de Airflow y MLflow | Diagrama del flujo |
| 15–35 | Ejecutar `docker compose up -d --build` y entrar a Airflow | Pantalla con DAG |
| 35–55 | Ejecutar manualmente el DAG | Grafo completo en verde |
| 55–75 | Abrir logs y revisar los tres runs en MLflow | Métricas y runs |
| 75–95 | Provocar fallo con `force_fail=True`, revisar logs y corregirlo | Captura del fallo y corrección |
| 95–110 | Modificar `schedule` y restaurar manual | Captura de configuración |
| 110–120 | Consultar `resultados/informe_airflow.md` y Champion | Informe y Registry |

## Actividad guiada

1. Descomprimir `05_airflow_rym_spotify.zip` y abrir carpeta en VS Code.
2. Verificar que Docker Desktop está en marcha.
3. Ejecutar en PowerShell `docker compose up -d --build`.
4. Ejecutar `docker compose ps` hasta que estén corriendo `mlflow`, `worker` y `airflow`.
5. Consultar la contraseña de Airflow según `README.md`.
6. Entrar a http://localhost:8080, buscar `rym_spotify_entrenamiento`, activarlo y seleccionar Trigger.
7. Abrir cada tarea en Airflow y observar la información en logs.
8. Entrar a http://localhost:5001: verificar tres runs y Champion de `RYM_Spotify_Favoritos`.
9. Modificar `force_fail=False` a `True` dentro del DAG y lanzar nueva ejecución; explicar por qué no se ejecutan las siguientes tareas.
10. Restaurar `False`; ejecutar el DAG y verificar éxito.
11. Cambiar temporalmente `schedule=None` por `schedule='@daily'`, observar y restaurar `None`.
12. Revisar en VS Code el informe y la comparación de métricas en `resultados/`.

## Entregar

Un PDF que incluya captura de Docker Compose, DAG con cinco tareas y éxito, log de entrenamiento, runs en MLflow, modelo Champion registrado, fallo deliberado, corrección y el archivo `informe_airflow.md`.

## Preguntas de reflexión

- ¿Qué diferencia existe entre registrar experimentos en MLflow y orquestar tareas con Airflow?
- ¿Por qué la selección del Champion se basa en F1 de validación cruzada y no en el test?
- ¿Qué ocurre con las tareas posteriores cuando falla `validar_csv`?
- ¿Qué ventaja tiene usar `schedule=None` durante la práctica?
