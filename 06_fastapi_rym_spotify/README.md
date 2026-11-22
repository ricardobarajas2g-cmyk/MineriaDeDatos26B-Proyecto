# Práctica 6 — FastAPI (RYM + Spotify)

Proyecto autocontenido para **Windows + VS Code**. Predice si un álbum tiene características asociadas con puntuación RYM **9–10**. Incluye CSV integrado, un pipeline logistic **ya entrenado**, HTML, API y pruebas.

**Modelo suministrado:** réplica local de Logistic Regression con el mismo preprocesamiento del proyecto de MLflow y partición de entrenamiento 80%, seed 42. **No es una exportación del Registry de tu ordenador.** Si deseas usar tu Champion exacto, seguir el apartado 5.

## 1. Preparación

- Python **3.11** instalado, editor VS Code.
- **No necesitas Airflow, Docker ni MLflow** para la ruta principal.
- Abrir `06_fastapi_rym_spotify` como carpeta raíz en VS Code.
- Terminal integrada **PowerShell** en esa carpeta (debe aparecer `requirements.txt` en `dir`).

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si Python 3.11 no está instalado, usar una versión compatible que tenga instaladores para las dependencias (`py --list`). Si se necesita reconstruir el artefacto por diferencias de versión, consultar el apartado 6.

## 2. Ejecutar pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## 3. Iniciar aplicación

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mantener esa terminal abierta. Abrir:
- Formulario: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs
- Salud: http://127.0.0.1:8000/health
- Ejemplos: http://127.0.0.1:8000/albums
- Metadatos de modelo: http://127.0.0.1:8000/model-info

## 4. Ejemplo de POST /predict

```json
{
  "artista": "1800HaightStreet",
  "album": "Endless",
  "generos_frecuentes": "dub techno | lo-fi house",
  "promedio_danceability": 0.667,
  "promedio_energy": 0.75031,
  "promedio_acousticness": 0.04021,
  "promedio_instrumentalness": 0.886,
  "promedio_valence": 0.15870,
  "promedio_tempo": 133.67,
  "promedio_popularity": 1.46154,
  "promedio_loudness": -10.76869,
  "anio_spotify": 2017
}
```

Usar `/docs` > `POST /predict` > `Try it out` > pegar JSON > `Execute`. La respuesta contiene `prediction` (0 o 1) y `probabilidad_favorito` entre 0 y 1. En el formulario, el selector de álbumes rellena automáticamente los campos musicales.

## 5. Opcional: utilizar tu Champion REAL de la Práctica 4 o 5

En el ZIP existe una **réplica local** que funciona sin MLflow. Para utilizar el modelo que registraste en tu propio MLflow:

1. Mantener ejecutándose el servidor MLflow. Práctica 4 normalmente en `http://127.0.0.1:5000`; Práctica 5 en `http://127.0.0.1:5001` (Docker Compose).
2. **Detener FastAPI** con Ctrl+C antes de exportar.
3. Instalar dependencias opcionales:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-mlflow-opcional.txt
```

4. Exportar el Champion (ejemplo desde Práctica 4):

```powershell
.\.venv\Scripts\python.exe -m scripts.exportar_champion_mlflow --tracking-uri http://127.0.0.1:5000
```

O desde Práctica 5:

```powershell
.\.venv\Scripts\python.exe -m scripts.exportar_champion_mlflow --tracking-uri http://127.0.0.1:5001
```

5. Volver a iniciar la API y comprobar `/model-info`. Esta operación **reemplaza** `models/champion.joblib` por un archivo del Champion registrado. Solo cargar modelos creados y controlados por fuentes confiables; MLflow `cloudpickle` utiliza deserialización de objetos Python. El modelo original queda sobrescrito: hacer una copia de respaldo antes, si se necesita.

Para usar la Práctica 5 en Docker, MLflow de esa práctica debe estar funcionando; no se necesita Airflow para hacer predicciones una vez exportado.

**Compatibilidad:** el modelo real puede haberse entrenado con otra versión de scikit-learn; lo más seguro es exportarlo y ejecutarlo en un entorno con versiones compatibles con su entrenamiento. Para volver al modelo preparado incluido, reinstalar el ZIP.

## 6. Reconstrucción opcional del modelo local

Si la versión instalada de scikit-learn es diferente de la del modelo distribuido, reconstruir localmente en el mismo entorno:

```powershell
.\.venv\Scripts\python.exe -m scripts.reconstruir_modelo
```

Este entrenamiento replica la partición del proyecto de MLflow: 80% training, 20% holdout; los datos de test **no intervienen** en el ajuste. No mide rendimiento ni selecciona hiperparámetros desde el holdout.

## 7. Registro de solicitudes (para Práctica 9)

Cada POST válido escribe una línea JSON en `logs/predicciones.jsonl`, incluyendo fecha, variables usadas y respuesta del modelo. Es una demostración local de monitoreo; no sirve como sistema de logs de producción y puede contener datos personales. No publicar logs en GitHub.

## Errores frecuentes

- `python.exe no se reconoce`: crear primero `.venv` y verificar que estás en la carpeta correcta.
- `ModuleNotFoundError`: instalar `requirements.txt` dentro del entorno virtual.
- `port 8000 occupied`: ejecutar con `--port 8001` y cambiar URL.
- Error al cargar `.joblib`: comprobar que el archivo existe, la versión de scikit-learn y reconstruir el modelo local si hace falta.
- Error HTTP 422: revisar que todos los campos musicales están presentes; rango de características 0–1 y año entre 1900 y 2100.

## Alcance

- Modelo de preferencias personales: predice probabilidades estimadas y no garantiza gustos futuros.
- Artista y título son metadatos **solo para mostrar**, no entradas usadas por el modelo.
- El selector de ejemplo usa álbumes existentes de RYM + Spotify; esos ejemplos pueden pertenecer al entrenamiento. No utilizar sus predicciones como una medida independiente de calidad.
- Dataset CSV: 618 álbumes, 611 con rating; entrada a la API: 9 variables numéricas + `generos_frecuentes`.
- No se entrena el modelo al realizar cada predicción.
