# Práctica 9 — Monitoreo con Evidently AI | RYM + Spotify

Proyecto **independiente** para continuar después de la Práctica 8. Analiza la distribución de las características musicales que llegan al endpoint `POST /predict` de FastAPI, comparándolas con el histórico de álbumes RYM + Spotify. Se generan un **reporte HTML Evidently**, JSON de métricas y resumen descriptivo. **No requiere reinstalar ni cargar el Champion de MLflow**: utiliza las entradas y salidas ya registradas por FastAPI.

El proyecto incluye el CSV original proporcionado para la práctica (618 álbumes, 23 columnas) y genera una referencia de **611 álbumes puntuados**; 7 registros sin calificación se excluyen. Se comparan las 9 variables numéricas de entrada más el **primer género** de `generos_frecuentes` (representación categórica para monitoreo; el modelo real utiliza toda la cadena de géneros).

> **Privacidad:** el CSV original, referencia, JSONL de predicciones y reportes están excluidos de Git por `.gitignore`. No incluirlos en un repositorio público ni publicar imágenes que los contengan. El `Dockerfile` deliberadamente no copia esos archivos: los monta como volúmenes locales.

## 1. Archivos del proyecto

```text
09_monitoring_rym_spotify/
├── monitoring/
│   ├── config.py              # 9 columnas numéricas, género y rangos de FastAPI
│   ├── datos.py               # CSV de referencia + lectura de logs JSONL
│   ├── preparar_datos.py      # genera la referencia de 611 álbumes
│   ├── generar_demo.py        # logs SINTÉTICOS para el ejemplo de drift
│   └── generar_reporte.py     # Evidently DataDriftPreset + HTML/JSON/Markdown
├── scripts/
│   ├── copiar_logs_practica8.ps1   # copia desde Práctica 6, 7, 8 o contenedor
│   └── generar_solicitudes_api.py  # OPCIONAL: POST /predict de prueba a localhost
├── data/
│   ├── rym_spotify_con_generos.csv # histórico original PRIVADO
│   ├── referencia_rym_spotify.csv  # referencia generada, SOLO features
│   ├── referencia_info.json        # metadatos referencia
│   └── demo_predicciones.jsonl     # 120 solicitudes sintéticas, NO hay predicciones
├── logs/                         # logs reales que copiarás desde FastAPI
├── reports/                      # reportes Evidently de salida
├── tests/
├── Dockerfile
├── compose.yaml
├── compose.fedora.yaml
├── requirements.txt
├── GUIA_ALUMNO.md
└── README.md
```

## 2. Inicio rápido en Windows 11 (PowerShell y VS Code)

Descomprimir junto a las carpetas `06_fastapi_rym_spotify`, `07_docker_rym_spotify` y `08_cicd_rym_spotify` dentro de `Proyecto/`. Abrir la carpeta `09_monitoring_rym_spotify` en VS Code.

Instalar Python **3.11** y dependencias:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Preparar baseline y datos de demostración (ambos **ya incluidos**, los comandos permiten reproducirlos):

```powershell
.\.venv\Scripts\python.exe -m monitoring.preparar_datos
.\.venv\Scripts\python.exe -m monitoring.generar_demo --escenario cambio --cantidad 120
```

Ejecutar el primer reporte con **datos de prueba sintéticos**:

```powershell
.\.venv\Scripts\python.exe -m monitoring.generar_reporte --log data/demo_predicciones.jsonl
Start-Process .\reports\drift_rym_spotify.html
```

Resultado: `reports/drift_rym_spotify.html` (panel de Evidently), `drift_evidently.json` (métricas originales), `resumen_monitoreo.json` y `resumen_monitoreo.md`. Al ejecutar nuevamente con otros logs se sobrescriben estos cuatro archivos; archivar una copia cuando sea necesario conservar las dos evidencias.

Ejecutar pruebas automatizadas:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Si aparece `ModuleNotFoundError: evidently`, comprobar que se instaló `requirements.txt` con el Python de `.venv`. **Evidently 0.7.19 usa `from evidently import Report, Dataset, DataDefinition` y `from evidently.presets import DataDriftPreset`.** Los ejemplos antiguos que importan desde `evidently.metric_preset` (API 0.6.x) no corresponden a este proyecto.

## 3. Monitorear registros reales de FastAPI

### Opción A — registros existentes como archivos locales

Si ejecutaste FastAPI fuera de Docker, el archivo usual está en `06_fastapi_rym_spotify/logs/predicciones.jsonl`. Si lo tienes localmente en la Práctica 7 u 8, también se puede usar. Importar desde PowerShell:

```powershell
.\scripts\copiar_logs_practica8.ps1
```

Si ya existe un archivo en la carpeta 9, el script evita sobrescribirlo; para reemplazarlo, usar `-Forzar`.

### Opción B — FastAPI dentro de Docker

Cuando los registros se guardan en un volumen Docker de la Práctica 7/8, **no aparecen necesariamente en la carpeta `logs/` de Windows**. Con la API **todavía en ejecución**, listar contenedores:

```powershell
docker ps --format "table {{.Names}}\t{{.Image}}"
```

Copiar desde el contenedor que sirve la API (sustituir por el nombre real):

```powershell
.\scripts\copiar_logs_practica8.ps1 -Contenedor NOMBRE_DEL_CONTENEDOR
```

Alternativa directa:

```powershell
docker cp NOMBRE_DEL_CONTENEDOR:/app/logs/predicciones.jsonl .\logs\predicciones.jsonl
```

Para un contenedor arrancado con `docker run --rm`, **copiar antes de detenerlo** si no se configuró un volumen persistente.

Para el monitoreo con registros copiados:

```powershell
.\.venv\Scripts\python.exe -m monitoring.generar_reporte --log logs/predicciones.jsonl
Start-Process .\reports\drift_rym_spotify.html
```

El script requiere **10 entradas válidas como mínimo** para ejecutar un reporte, y avisa si hay menos de 30. La referencia histórica de 611 observaciones se mantiene igual; las solicitudes repetidas por pruebas pueden sesgar los resultados de drift.

### Opción C — generar consultas de PRUEBA con respuestas del Champion

Si necesitas más solicitudes para practicar la integración completa, primero ejecuta la API real de Práctica 8 en `http://127.0.0.1:8001`. Desde Práctica 9:

```powershell
.\.venv\Scripts\python.exe -m scripts.generar_solicitudes_api --url http://127.0.0.1:8001 --cantidad 50 --escenario similar
```

Esta acción envía solicitudes al modelo real, por lo que FastAPI guarda respuestas reales; la entrada se identifica con `artista: "[SIMULACION API]"`. Para ensayar drift más notable, ejecutar `--escenario cambio` (se fuerzan valores altos de energía, bajos de acústica y años recientes). El archivo extraído se marcará como `simulacion_api` en el resumen. **Estas consultas son un experimento, no tráfico real de usuarios.**

## 4. Ejecutar Evidently mediante Docker (Windows o Fedora)

Docker instala las dependencias y genera el reporte sin usar el Python local:

```powershell
docker compose build
docker compose run --rm monitor python -m monitoring.generar_reporte --log data/demo_predicciones.jsonl
```

Para logs reales ya copiados a `logs/`:

```powershell
docker compose run --rm monitor
```

Los reportes se crean en `reports/` **del equipo anfitrión**. El servicio es una tarea de ejecución única; `docker compose run --rm` es adecuado y el contenedor termina después de producir el HTML.

### Fedora Linux

Con Docker Engine y Compose instalados, desde la carpeta:

```bash
docker compose build
docker compose run --rm monitor python -m monitoring.generar_reporte --log data/demo_predicciones.jsonl
```

Para sistemas Fedora que requieren permisos SELinux sobre los volúmenes vinculados, se incluye el archivo `compose.fedora.yaml` con los marcadores `:Z`:

```bash
docker compose -f compose.yaml -f compose.fedora.yaml build
docker compose -f compose.yaml -f compose.fedora.yaml run --rm monitor python -m monitoring.generar_reporte --log data/demo_predicciones.jsonl
```

Si Docker requiere privilegios, anteponer `sudo` a los comandos. Los reportes podrían quedar con propietario `root`; usar `sudo chown -R "$(id -u):$(id -g)" reports/` para abrirlos/guardarlos desde el usuario normal.

Para importar los logs del contenedor de FastAPI en Fedora, localizarlo y copiar mientras se ejecuta:

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}'
docker cp NOMBRE_DEL_CONTENEDOR:/app/logs/predicciones.jsonl ./logs/predicciones.jsonl
docker compose run --rm monitor
```

Si se utiliza el override SELinux, incluir ambos archivos `-f` también en ese último comando.

## 5. Qué interpreta el reporte

- **Data drift:** compara la distribución de `promedio_energy`, `promedio_acousticness`, `promedio_danceability`, `promedio_instrumentalness`, `promedio_valence`, `promedio_tempo`, `promedio_popularity`, `promedio_loudness` y `anio_spotify`, además de `genero_principal`.
- **Calidad de ingesta:** cuenta líneas erróneas, IDs duplicados y solicitudes fuera de los rangos de FastAPI.
- **Predicciones:** cuando hay respuesta del modelo, resume clase `0/1`, proporción de favoritos predichos y probabilidad estimada media/mediana. El archivo `demo_predicciones.jsonl` no incluye salidas inventadas.
- **Calidad del modelo:** un cambio de datos puede motivar investigación o actualización de la referencia; no se puede afirmar que el F1 disminuyó sin nuevas calificaciones reales de RYM. Tampoco se infiere que un álbum sea favorito por tener probabilidad alta sin observar la calificación real.

**Comparación de referencia:** se usan los **611 álbumes puntuados** del histórico, porque son una base disponible y reproducible sin cargar la versión exacta del modelo. El entrenamiento original de la Práctica 4 utilizó una división 80/20 (488 entrenamiento, 123 prueba). El baseline de esta práctica es histórico y **no equivale exactamente al subconjunto de entrenamiento**. Para una auditoría estricta de drift en producción, convendría almacenar el subconjunto de entrenamiento original.

**Recomendación para el informe:** generar primero un reporte sobre `--escenario similar` y guardar la captura; luego otro con `--escenario cambio` y explicar qué variables cambiaron. Finalmente, si hay registros reales suficientes, generar el reporte sobre `logs/predicciones.jsonl` y comparar.

## 6. Opciones disponibles

```bash
python -m monitoring.preparar_datos --csv data/rym_spotify_con_generos.csv --salida data/referencia_rym_spotify.csv
python -m monitoring.generar_demo --cantidad 120 --escenario similar --salida data/demo_similar.jsonl
python -m monitoring.generar_demo --cantidad 120 --escenario cambio --salida data/demo_cambio.jsonl
python -m monitoring.generar_reporte --referencia data/referencia_rym_spotify.csv --log data/demo_cambio.jsonl --salida reports
python -m monitoring.generar_reporte --log logs/predicciones.jsonl --solo-reales
python -m monitoring.generar_reporte --log logs/predicciones.jsonl --minimo 5  # solo experimentos de muestra muy pequeña
```

El argumento `--solo-reales` impide generar un reporte si se detectan consultas marcadas como demostración. Otras consultas manuales de prueba que carezcan de marcador serán indistinguibles de datos reales: utilizar logs con procedencia conocida.

## 7. Evidencias de entrega

1. Preparación del baseline: 611 filas válidas y 10 características monitoreadas.
2. `pytest -v` exitoso.
3. Reporte HTML de Evidently con ejemplo de drift y explicación de al menos 3 variables.
4. Reporte `resumen_monitoreo.json` que distinga datos reales de demostración.
5. Ejecución con Docker en Windows y/o Fedora (captura de comando y HTML generado).
6. Explicación breve de acciones ante drift: revisar origen de consultas, calidad, etiquetar álbumes, medir F1 y decidir si reentrenar.

## Solución de problemas

- **`No se encontró referencia`:** `python -m monitoring.preparar_datos`.
- **`Logs no encontrados`:** copiar desde FastAPI mientras corre o usar `--log data/demo_predicciones.jsonl`.
- **`Solo hay 1 solicitud válida`:** acumular al menos 10 o usar demo; preferir 30+ para discutir estadística.
- **`Permission denied` en Fedora:** verificar bind mounts; usar `compose.fedora.yaml` para SELinux.
- **`ModuleNotFoundError: evidently`:** instalar `requirements.txt` en el mismo entorno con Python 3.11.
- **HTML sin valores de clases/probabilidades:** ocurre con el demo sintético; para estudiar predicciones usar logs con respuestas reales de FastAPI.
- **Conflicto de scikit-learn 1.8/1.9:** no aplica al monitoreo offline porque no deserializa ni ejecuta `champion.joblib`.

## Referencias de API

- Evidently 0.7.x: [Report, Dataset, DataDefinition](https://evidentlyai.github.io/evidently/api-reference/v0.7.19/evidently.html)
- [Presets, incluido DataDriftPreset](https://evidentlyai.github.io/evidently/api-reference/v0.7.19/evidently/presets.html)
- [Snapshot.save_html, Snapshot.save_json](https://evidentlyai.github.io/evidently/api-reference/v0.7.19/evidently/core/report.html)
