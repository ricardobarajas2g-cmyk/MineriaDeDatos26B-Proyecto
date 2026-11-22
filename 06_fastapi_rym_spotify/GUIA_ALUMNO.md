# Guía del alumno · Práctica 6 — FastAPI con álbumes RYM + Spotify (120 minutos)

## Objetivo

Utilizar un modelo de clasificación de favoritos (RYM 9–10) desde una API REST. Se proporciona todo el código y el modelo; la práctica se centra en endpoints, validación, JSON y consumo desde HTML.

| Tiempo | Actividad | Evidencia |
|---|---|---|
| 0–15 min | Analizar flujo HTML → FastAPI → modelo | Esquema del flujo |
| 15–30 min | Instalar dependencias y ejecutar pytest | Tests en verde |
| 30–50 min | Ejecutar Uvicorn y abrir `/docs` | Interfaz Swagger |
| 50–70 min | Probar `POST /predict` con un álbum real | JSON de respuesta |
| 70–90 min | Probar selector HTML y cambiar energía/valencia | Dos predicciones |
| 90–105 min | Provocar HTTP 422 con energía 1.5 y revisar validaciones | Error 422 |
| 105–120 min | Examinar `/health`, `/model-info`, logs y entregable | Registro JSONL |

## Paso a paso

1. Descomprimir `06_fastapi_rym_spotify.zip`, abrir carpeta en VS Code y leer `README.md`.
2. Crear entorno e instalar paquetes según README. Ejecutar `python -m pytest -v` desde `.venv`.
3. Iniciar Uvicorn y visitar `http://127.0.0.1:8000/docs`.
4. Probar `POST /predict` con el JSON del README (el álbum *Endless* de 1800HaightStreet).
5. En `http://127.0.0.1:8000/` seleccionar otro álbum del catálogo, pulsar **Predecir favorito**.
6. Modificar solo `promedio_energy` (por ejemplo, 0.2), repetir, anotar ambas probabilidades. No tienen por qué cambiar mucho.
7. En `/docs`, enviar energía 1.5 y comprobar que FastAPI responde **422** con detalles de validación.
8. Abrir `logs/predicciones.jsonl`; observar una línea por solicitud válida con `request` y `response`.
9. Consultar `/health` y `/model-info` y explicar qué indica cada uno.
10. (Opcional) Con MLflow funcionando, exportar el Champion real mediante `scripts.exportar_champion_mlflow` y comprobar `/model-info`.

## Modificación opcional controlada

En `app/main.py`, modifica únicamente las etiquetas de `interpretacion` para que la respuesta muestre `Favorito estimado` o `No favorito estimado`. Guarda el archivo; Uvicorn con `--reload` detectará el cambio. Ejecuta otra predicción desde `/docs`.

## Entregable

Capturas de: servidor activo, documentación `/docs`, respuesta de una predicción, predicción HTML, error 422, `/health`, `/model-info`, fragmento de `logs/predicciones.jsonl`. Incluir una tabla con dos valores de energía y dos probabilidades del mismo álbum.

## Preguntas de reflexión

- ¿Por qué FastAPI necesita un esquema de entrada?
- ¿Qué diferencia hay entre `POST /predict` y `GET /health`?
- ¿Por qué el título y el artista aparecen en la respuesta pero no influyen en la predicción?
- ¿Por qué no se debe evaluar el F1 usando ejemplos que podrían estar en entrenamiento?
- ¿Qué información sería necesaria para monitorear el desempeño cuando lleguen calificaciones RYM reales?
