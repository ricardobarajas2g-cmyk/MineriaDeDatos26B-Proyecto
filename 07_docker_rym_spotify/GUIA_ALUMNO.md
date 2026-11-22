# Guía del alumno — Práctica 7: Docker para RYM + Spotify (120 min)

## Propósito

Ejecutar la API de preferencias musicales construida en la Práctica 6 dentro de un contenedor Docker. No se programarán modelos nuevos; el ZIP incluye el código, el HTML y un modelo funcional. Opcionalmente, se incorporará el Champion exacto exportado de MLflow en la Práctica 6.

| Tiempo | Actividad | Evidencia |
|---|---|---|
| 0–15 min | Comprobar Docker Desktop y carpeta raíz | `docker version`, archivos presentes |
| 15–30 min | Interpretar el Dockerfile y `compose.yaml` | Explicar `FROM`, `COPY`, `RUN`, `CMD`, `ports` |
| 30–55 min | Construir imagen y levantar contenedor | `docker compose up -d --build` |
| 55–75 min | Probar `/`, `/docs`, `/predict` y `/health` en 8001 | Predicción JSON, HTTP 200 |
| 75–90 min | Observar logs, detener/iniciar y verificar persistencia | `docker compose logs`, `stop`, `start` |
| 90–105 min | Copiar Champion de la práctica 6 y reconstruir | `/model-info` con versión apropiada |
| 105–115 min | Provocar error controlado (puerto ocupado o respuesta 422) y recuperarlo | Error/corrección |
| 115–120 min | Entregable y limpieza | `docker compose down` |

## Instrucciones

1. Abrir `07_docker_rym_spotify` en VS Code y Docker Desktop con contenedores Linux. Abrir PowerShell en esa carpeta.
2. Ejecutar `docker --version` y `docker compose version`.
3. Abrir `Dockerfile`: localizar la imagen base, instalación de dependencias, copia del modelo y comando de inicio; observar cómo el contenedor escucha en el 8000.
4. Abrir `compose.yaml`: identificar mapeo `127.0.0.1:8001:8000`, healthcheck y volumen de registros.
5. Ejecutar `docker compose up -d --build` y `docker compose ps`. Si falla, abrir `docker compose logs --tail 100 api`.
6. Abrir http://127.0.0.1:8001/ y seleccionar *Aphex Twin — Selected Ambient Works Volume II* u otro álbum de muestra; enviar predicción. Abrir también `/docs` y `/health`.
7. En segunda terminal: `py -3.11 scripts/probar_contenedor.py` para comprobar cuatro endpoints y una predicción.
8. Inspeccionar registros con `docker compose logs --tail 50 api` y observar la salida de `predicciones.jsonl` con el comando de README.
9. Ejecutar `docker compose stop` y verificar que la web no responde. Ejecutar `docker compose start` y verificar que vuelve a responder. Comprobar que el volumen mantiene la línea de predicción.
10. Opcional **para tu proyecto personal**: ejecutar `.\scripts\importar_champion_practica6.ps1` (si lo permite PowerShell) o copiar manualmente `models/champion.joblib` y `models/model_info.json` desde la Práctica 6. Establecer `SKLEARN_VERSION=1.9.1` y reconstruir. Revisar `/model-info`.
11. Error controlado: enviar por `/docs` `promedio_energy=1.5`. La API debe devolver HTTP 422, porque la energía válida va de 0 a 1. Corregir a 0.5 y repetir.
12. Detener contenedor con `docker compose down`, conservando logs en el volumen.

## Entregable

Incluir 7 capturas: (1) Docker version; (2) Dockerfile y Compose; (3) construcción/imagen; (4) `docker compose ps` healthy; (5) predicción en el formulario o en `/docs`; (6) logs del contenedor y registro JSONL; (7) `/model-info`, preferentemente con Champion real de la Práctica 6. Escribir 3–5 líneas sobre la diferencia entre imagen, contenedor, puerto y volumen.

## Preguntas de reflexión

- ¿Por qué dentro del contenedor Uvicorn escucha en `0.0.0.0:8000` y desde Windows se accede a `127.0.0.1:8001`?
- ¿Por qué modificar el modelo requiere reconstruir la imagen?
- ¿Dónde quedan las predicciones registradas cuando se elimina el contenedor?
- ¿Por qué la versión de scikit-learn debe corresponder a la usada al entrenar el Champion?
- ¿Por qué no es necesario ejecutar MLflow para predecir después de empaquetar el Champion?
