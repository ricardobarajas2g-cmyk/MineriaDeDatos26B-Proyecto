# Práctica 5 — Airflow + MLflow con RYM + Spotify

Esta práctica reproduce **exactamente el problema y la lógica de entrenamiento de la Práctica 4**: 611 álbumes etiquetados de `rym_spotify_con_generos.csv`, clasificadores Logistic Regression / Random Forest / SVM, selección por F1 promedio en validación cruzada. Los scripts originales `src/` se reutilizan y Airflow solamente organiza la ejecución.

## Requisitos

- Windows 10/11 con **Docker Desktop** iniciado y contenedores **Linux** habilitados.
- VS Code y terminal **PowerShell**; no es necesario instalar Airflow ni Python en Windows.
- Conexión a Internet **en la primera construcción** para descargar imágenes y paquetes.
- Se recomiendan al menos 6 GB de memoria disponible para Docker y espacio libre para imágenes.

## 1. Iniciar todo desde la carpeta descomprimida

En **PowerShell dentro de VS Code**:

```powershell
docker --version
docker compose version
docker compose up -d --build
docker compose ps
```

También se puede usar `iniciar_windows.bat`.

Al iniciar por primera vez, se descargan las imágenes; esto no sucede instantáneamente. Cuando los servicios estén levantados:

- **Airflow:** http://localhost:8080
- **MLflow de esta práctica:** http://localhost:5001

**Importante:** MLflow corre internamente en `http://mlflow:5000` y se publica al anfitrión en **5001** para no chocar con el servidor anterior de Práctica 4 en 5000. Esta práctica crea un **registro MLflow separado**, con sus propios runs y versiones de modelos; no modifica el registro anterior.

### Entrar en Airflow

Usuario: `admin`. Obtén la contraseña autogenerada con:

```powershell
docker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated
```

Si todavía no existe, revisar `docker compose logs airflow` y esperar a que arranque completamente. La cuenta `admin` se configura con los privilegios de administrador solo para el laboratorio local.

## 2. Ejecutar el DAG

1. Abrir `http://localhost:8080` e iniciar sesión.
2. Buscar `rym_spotify_entrenamiento` en la lista de DAGs.
3. Seleccionar **Trigger** (ejecución manual); `schedule=None` impide ejecuciones automáticas.
4. Abrir la vista de grafo y observar las cinco tareas:

```text
validar_csv -> preparar_datos -> entrenar_modelos -> registrar_champion -> generar_reporte
```

5. Comprobar que todas pasan a estado **success**.
6. Abrir http://localhost:5001 y verificar `RYM_Spotify_Favoritos`, sus **tres runs** y el modelo `RYMSpotifyClasificadorFavoritos` con alias `champion`.
7. En VS Code abrir `resultados/informe_airflow.md` y `resultados/comparacion_modelos.csv`.

## 3. Provocar un fallo controlado

Abrir `dags/rym_spotify_airflow_dag.py` y buscar:

```python
op_kwargs={"task": "validate", "force_fail": False},
```

Cambiar temporalmente a `True`, **guardar**, esperar a que Airflow recargue el DAG y activar una **nueva** ejecución. La tarea `validar_csv` fallará intencionalmente con código HTTP 422 y se detendrán las tareas posteriores. Revisar los logs. Restaurar `False`, guardar y lanzar otra ejecución. 

## 4. Modificar la programación

En el DAG, reemplazar temporalmente `schedule=None` por `schedule="@daily"` y comprobar la programación; **volver a None** para evitar ejecuciones diarias reales del entrenamiento.

## 5. Comprobar el modelo registrado (ejercicio extra)

```powershell
docker compose exec worker python -c "from worker.service import verify; print(verify())"
```

## 6. Detener los servicios

```powershell
docker compose down
```

Este comando **mantiene** los datos del volumen de MLflow y Airflow. Para reiniciar desde cero se pueden eliminar los volúmenes, **solo después de respaldar los resultados**:

```powershell
docker compose down -v
```

## Problemas comunes

- `port is already allocated 8080`: cerrar otro Airflow o modificar el puerto anfitrión de `compose.yaml`.
- `port is already allocated 5001`: cambiar solo el puerto anfitrión `127.0.0.1:5001:5000` (por ejemplo, `5002:5000`).
- No aparece el DAG: ejecutar `docker compose logs airflow --tail 100`, revisar que el contenedor terminó de iniciar y abrir los import errors de Airflow.
- Un modelo falló: abrir logs de `entrenar_modelos` en Airflow y `docker compose logs worker --tail 100`.
- MLflow no responde: `docker compose logs mlflow --tail 100`.
- Para ver logs de todos los servicios: `docker compose logs -f --tail 30`.
- `cloudpickle` avisa sobre deserialización: cargar únicamente modelos generados por este proyecto y de fuentes confiables.
- El warning de enteros y `SVC(probability=True)` viene de scikit-learn/MLflow y no impide completar este laboratorio.

## Arquitectura y por qué hay tres servicios

- `airflow`: gestiona DAGs, estados, dependencias y logs. **No instala scikit-learn**.
- `worker`: ejecuta el mismo código Python de la Práctica 4 y envía métricas a MLflow mediante la red Docker privada.
- `mlflow`: registra métricas, artefactos y versiones en Model Registry.

La API del `worker` no tiene puerto publicado fuera de Docker y no requiere autenticación; es exclusivamente **una simulación educativa local**, no un servicio de producción. Tampoco se publica Airflow ni MLflow en interfaces de red externas: están enlazados a `127.0.0.1`.

El CSV contiene preferencias musicales personales. Publicarlo en un repositorio GitHub público es decisión del propietario; no se publica automáticamente.

## Material de consulta

- Apache Airflow en Docker: https://airflow.apache.org/docs/apache-airflow/3.3.1/howto/docker-compose/
- Operadores Python en Airflow 3: https://airflow.apache.org/docs/apache-airflow-providers-standard/stable/operators/python.html
- MLflow Tracking Server: https://mlflow.org/docs/latest/tracking/server/

## Verificación local sin Docker (opcional)

```powershell
py -m pip install -r requirements-worker.txt
py -m pytest -q
py -m src.train --sin-mlflow
```

Este modo únicamente verifica los scripts y no realiza orquestación Airflow ni registra modelos en MLflow. El entorno Docker contiene las dependencias para la práctica completa.
