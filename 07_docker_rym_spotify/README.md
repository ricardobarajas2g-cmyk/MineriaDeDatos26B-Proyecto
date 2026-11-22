# Práctica 7 — Docker aplicado a RYM + Spotify

**Proyecto ejecutable para Windows + VS Code + Docker Desktop.** Es la misma API REST de la Práctica 6 con un `Dockerfile` y `compose.yaml` listos para construir y arrancar un contenedor. Permite clasificar álbumes como favorito probable (puntuación RYM 9–10) mediante características de audio y género.

## Contenido

- `app/`, `templates/`: aplicación FastAPI, HTML, endpoints `/`, `/predict`, `/health`, `/model-info`, `/albums`.
- `models/champion.joblib`: **modelo funcional incluido**, réplica local de Regresión Logística con scikit-learn **1.8.0**. **NO es tu Champion remoto de MLflow**; puedes sustituirlo por el Champion ya exportado en tu Práctica 6.
- `models/model_info.json`: versión scikit-learn y procedencia del modelo.
- `data/rym_spotify_con_generos.csv`: CSV integrado utilizado en el proyecto (618 filas, 611 con puntuaciones válidas).
- `data/albumes_ejemplo.json`: 40 álbumes para el formulario. Solo este JSON se copia a la imagen; el CSV completo queda en la carpeta entregada y no se necesita para inferencia.
- `Dockerfile`: construcción con Python 3.11 y dependencias; copia modelo y código a imagen.
- `compose.yaml`: mapea puerto **8001** del PC al **8000** interno; persiste logs en un volumen Docker; configura healthcheck.
- `.env.example`: versión de scikit-learn y puerto configurable.
- `GUIA_ALUMNO.md`: actividad de dos horas y capturas solicitadas.
- `scripts/probar_contenedor.py`: prueba integral de `/health`, `/model-info`, `/albums`, `/predict` con librería estándar.

## 1. Requisitos

- Docker Desktop instalado, iniciado y configurado con contenedores Linux.
- Visual Studio Code y terminal PowerShell.
- **No se requiere instalar las dependencias de Python localmente para ejecutar Docker.** Tampoco Airflow ni MLflow necesitan estar abiertos para correr la imagen una vez que el modelo está dentro.

## 2. Iniciar con el modelo INCLUIDO (funciona sin copiar otros archivos)

Abre **la carpeta raíz** `07_docker_rym_spotify` en VS Code. Comprueba que `compose.yaml` y `Dockerfile` aparecen en `dir`. En PowerShell, ejecuta:

```powershell
docker --version
docker compose version
docker compose up -d --build
docker compose ps
```

La primera construcción descargará Python e instalará dependencias dentro de la imagen. Espera a que el servicio figure `healthy` en `docker compose ps` (usa `docker compose logs -f api` para inspeccionar el arranque).

Abre en tu PC:

- Formulario HTML: http://127.0.0.1:8001/
- Swagger: http://127.0.0.1:8001/docs
- Estado: http://127.0.0.1:8001/health
- Metadatos: http://127.0.0.1:8001/model-info
- Álbumes disponibles: http://127.0.0.1:8001/albums?limit=5

**Nota:** El puerto 8001 evita interferir con FastAPI de la Práctica 6, que se ejecutaba en el 8000. Internamente, el contenedor escucha en el 8000.

## 3. Usar TU Champion real de la Práctica 6 (recomendado en tu caso)

Tu Práctica 6 **ya exportó el Champion real** desde MLflow de la Práctica 5. No se necesita volver a levantar MLflow ni Airflow: basta con copiar los dos archivos locales.

**Ruta automática si `06_fastapi_rym_spotify` y `07_docker_rym_spotify` son carpetas hermanas:**

```powershell
.\scripts\importar_champion_practica6.ps1
docker compose up -d --build --force-recreate
```

Este script copia `models/champion.joblib` y `models/model_info.json` desde la Práctica 6, y configura `.env` con `SKLEARN_VERSION` extraída de ese metadato. Para tu Champion de MLflow, la versión observada era **1.9.1**. Si PowerShell impide ejecutar el script, usa la ruta manual de abajo.

**Ruta manual sin ejecutar scripts `.ps1`:**

```powershell
Copy-Item ..\06_fastapi_rym_spotify\models\champion.joblib .\models\champion.joblib -Force
Copy-Item ..\06_fastapi_rym_spotify\models\model_info.json .\models\model_info.json -Force
Copy-Item .env.example .env
```

Edita `.env`: deja `SKLEARN_VERSION=1.9.1` (o la versión reportada por `/model-info` en tu Práctica 6) y `APP_PORT=8001`. Después:

```powershell
docker compose up -d --build --force-recreate
```

La nueva imagen incorporará **tu modelo real**. Entra a http://127.0.0.1:8001/model-info para comprobar `tipo: Champion exportado de MLflow` y `sklearn_version: 1.9.1`.

**IMPORTANTE:** El Dockerfile instala scikit-learn en la versión declarada por `SKLEARN_VERSION`. Evita cargar un `.joblib` entrenado con una versión distinta de la instalada. En el ZIP, los defaults `1.8.0` coinciden con el artefacto de ejemplo; al usar el Champion 1.9.1 debes actualizar `.env` como se indicó.

Si el archivo `.env` se guarda en Windows desde PowerShell, verifica con `Get-Content .env` que tenga `SKLEARN_VERSION=...` y `APP_PORT=...`.

## 4. Comprobar la API Docker

Abre `/` y elige un álbum. Usa **Predecir favorito**. La respuesta incluirá el nombre de modelo, clase 0 o 1 y probabilidad. Los metadatos `artista`/`album` son descriptivos y no participan en la predicción.

Para validar desde una segunda terminal (Python disponible por haber cursado Práctica 6):

```powershell
py -3.11 scripts/probar_contenedor.py
```

Si `py -3.11` no está disponible, también funciona con `python scripts/probar_contenedor.py`.

O prueba directamente desde `/docs` con `POST /predict`. El formulario usa `step="any"` en decimales para aceptar la precisión de Spotify.

## 5. Observación de contenedores, logs y persistencia

```powershell
docker compose ps
docker compose logs --tail 50 api
docker compose stop
docker compose start
docker compose ps
```

El registro de solicitudes y respuestas se guarda en el volumen nombrado `predicciones` de Docker. Para ver las últimas líneas:

```powershell
docker compose exec api python -c "from pathlib import Path; p=Path('/app/logs/predicciones.jsonl'); print(p.read_text(encoding='utf-8')[-2500:] if p.exists() else 'Sin predicciones todavía')"
```

Los datos del volumen sobreviven `docker compose down` y a volver a crear el contenedor. **`docker compose down -v` sí elimina el volumen y sus logs**.

Para copiar el log a la carpeta `logs/` en tu PC:

```powershell
New-Item -ItemType Directory -Force .\logs | Out-Null
docker compose cp api:/app/logs/predicciones.jsonl .\logs\predicciones.jsonl
```

## 6. Construir una segunda versión de imagen (opcional)

Modifica el título de FastAPI en `app/main.py` (parámetro `title=`), sin cambiar el modelo. Reconstruye y conserva la imagen etiquetada:

```powershell
docker compose build
docker tag rym-spotify-api:local rym-spotify-api:v2
docker image ls rym-spotify-api
docker compose up -d --force-recreate
```

Si quieres mantener también el estado inicial como `v1`, etiqueta la imagen **antes de modificar archivos**: `docker tag rym-spotify-api:local rym-spotify-api:v1`.

## 7. Limpiar

```powershell
docker compose down
```

Esto detiene y elimina el contenedor y la red, conservando imágenes y los registros del volumen.

## Problemas frecuentes

| Síntoma | Qué revisar |
|---|---|
| `docker ... no se reconoce` | Instalar Docker Desktop y reiniciar terminal |
| `Cannot connect to Docker daemon` | Iniciar Docker Desktop y esperar que indique Engine running |
| `port is already allocated` | Modificar `APP_PORT=8002` en `.env`; abrir localhost:8002 |
| Contenedor `unhealthy` o `exited` | `docker compose logs --tail 100 api` |
| Warning versión scikit-learn | Revisar `models/model_info.json` y `SKLEARN_VERSION` en `.env`; reconstruir imagen |
| HTTP 422 | Revisar las variables obligatorias; géneros con `|`, valores 0–1, etc. |
| Cambias `champion.joblib` y parece el modelo anterior | Volver a construir: `docker compose up -d --build --force-recreate` |

## Alcance y reproducibilidad

- Proyecto académico, **sin uso de clientes reales**; modelo personal entrenado sobre tu colección RYM + Spotify.
- `joblib` requiere confiar en el origen del modelo; nunca cargar archivos obtenidos de fuentes desconocidas.
- Los ejemplos pueden estar en entrenamiento; no sirven para recalcular F1 de test.
- Contenedores Linux comparten kernel del entorno Linux gestionado por Docker Desktop. No se necesita instalar Python/scikit-learn en Windows para ejecutar la API dentro del contenedor.
- Un equipo con Docker compatible puede ejecutar la imagen, siempre que su arquitectura y dependencias sean compatibles.
