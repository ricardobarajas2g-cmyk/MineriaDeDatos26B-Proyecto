# Notas docentes — Práctica 7

- Es una continuación directa de la **Práctica 6 real**. API y validaciones son las mismas, se corrige `step=any` en el formulario para decimales Spotify.
- La imagen incluye código `app/`, `src/config.py`, `models/` y los ejemplos. El dataset CSV está en el ZIP para documentación pero **no dentro de la imagen**.
- `SKLEARN_VERSION=1.8.0` por defecto **es compatible con el modelo local incluido**. Para que el estudiante use el Champion que ya exportó de MLflow (scikit-learn 1.9.1), copiar dos archivos de `06_fastapi_rym_spotify/models` y cambiar `.env` a 1.9.1 (o ejecutar el script PowerShell incluido). La copia del Champion verdadero no se puede realizar desde este ZIP sin acceso al disco del alumno.
- Docker Compose escucha **solo en 127.0.0.1** y usa puerto 8001 para que se pueda comparar lado a lado con la Práctica 6 (8000).
- Volumen nombrado `predicciones`: enseña persistencia; no usar `docker compose down -v` antes de revisar logs.
- Si el usuario decide actualizar manualmente HTML/fastapi, siempre reconstruir imagen (no se habilita autoreload ni bind mounting de código).
- El criterio final es que `/health` devuelve JSON, `/predict` devuelve clase/probabilidad y `/model-info` acredita procedencia del artefacto.
- Docker Engine no está instalado en el entorno de creación; se han validado pruebas Python, archivos YAML, ZIP y contratos de la API, pero no una ejecución real `docker build`.
