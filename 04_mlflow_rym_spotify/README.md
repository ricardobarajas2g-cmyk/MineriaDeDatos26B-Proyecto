# Práctica 4 — MLflow con álbumes RYM + Spotify

**Duración:** 2 horas · **Sistema:** Windows 10/11 · **Editor:** VS Code · **Python recomendado:** 3.11 x64.

## Pregunta del proyecto

¿Se puede predecir si un álbum recibirá una calificación de 9 o 10 en RYM a partir de características musicales y géneros? 

El CSV original `data/rym_spotify_con_generos.csv` contiene 618 álbumes. Se excluyen los 7 sin puntuación. La clasificación final tiene **611 álbumes (291 favoritos y 320 no favoritos)**.

**Variable objetivo:** `favorito_9_10` (1 = puntuación 9–10; 0 = puntuación 1–8).

**Entradas:** energía, acústica, instrumentalidad, bailabilidad, valencia, tempo, volumen, popularidad, año de Spotify y géneros. Los géneros están separados por `|`. El código los convierte en variables binarias por género con `CountVectorizer` dentro del pipeline. No se utiliza la puntuación RYM, ni la cantidad o proporción de canciones con Me gusta para predecir.

## 1. Abrir en VS Code

Descomprimir `04_mlflow_rym_spotify.zip`. Abrir **la carpeta que contiene** `src`, `data` y este README. Abrir Terminal → New Terminal. Comandos válidos en PowerShell o CMD:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.prepare_data
```

Si `py -3.11` no funciona, usar `py -m venv .venv` o `python -m venv .venv` siempre que apunte a Python 3.11. No hace falta activar el entorno virtual, por lo que no hay que modificar la política de PowerShell.

**Resultado esperado del script de datos:** 611 filas etiquetadas. Se generan archivos en `resultados/`.

## 2. Abrir servidor MLflow — terminal 1

Desde la carpeta principal del proyecto:

```powershell
.\.venv\Scripts\python.exe -m mlflow server --backend-store-uri sqlite:///mlflow.db --artifacts-destination ./mlartifacts --host 127.0.0.1 --port 5000
```

También puede ejecutarse `iniciar_mlflow_windows.bat` con doble clic. Mantener esa terminal abierta. Entrar a **http://127.0.0.1:5000**. Se usará SQLite para los runs y Model Registry, y `mlartifacts/` para modelos, gráficos y reportes.

## 3. Entrenar y registrar modelos — terminal 2

```powershell
.\.venv\Scripts\python.exe -m src.train
```

Se crean tres runs en el experimento `RYM_Spotify_Favoritos`: `logistic`, `forest` y `svm`. Cada run almacena hiperparámetros, métricas de validación cruzada, métricas del conjunto de prueba, matriz de confusión, curva ROC y un pipeline serializado. La validación cruzada consta de 5 folds dentro de entrenamiento (80% de las filas). El test (20%) se reserva como evaluación independiente.

Si se desea comprobar entrenamientos antes de iniciar MLflow:

```powershell
.\.venv\Scripts\python.exe -m src.train --sin-mlflow
```

Ese comando entrena y genera comparaciones **pero no crea runs**; repetir sin `--sin-mlflow` para verlos en la interfaz.

### Qué comparar en MLflow

En la pestaña de experimentos, marcar los tres runs y pulsar **Compare**. Comparar `cv_f1_mean`, `cv_roc_auc_mean`, `test_accuracy`, `test_precision`, `test_recall`, `test_f1`, `test_roc_auc`.

**Regla de elección:** mayor `cv_f1_mean` (calculada únicamente sobre entrenamiento). No seleccionar en función del test.

## 4. Registrar Champion en Model Registry

```powershell
.\.venv\Scripts\python.exe -m src.register_champion
```

Esto registra el mejor pipeline en `RYMSpotifyClasificadorFavoritos` y le asigna el alias `champion`. Abrir la pestaña **Models** de MLflow y confirmar el alias.

## 5. Cargar el Champion y predecir

```powershell
.\.venv\Scripts\python.exe -m src.verify_champion --index 0
```

El ejemplo utiliza una fila del CSV para comprobar técnicamente la carga del modelo. La probabilidad se interpreta como estimación de pertenencia a la clase 1, sin una garantía de calibración.

## 6. Entregable del alumno

Enviar un PDF con: (1) `pytest` correcto; (2) CSV preparado y recuento de clases; (3) tres runs en MLflow; (4) métricas e hiperparámetros; (5) comparación y elección de Champion por `cv_f1_mean`; (6) curva ROC y matriz de confusión; (7) versión en Model Registry con alias `champion`; (8) prueba de predicción desde Registry.

**Salida adicional:** `resultados/comparacion_modelos.csv` y `resultados/resumen_experimento.json`.

## Interpretación y buenas prácticas

- F1 combina Precision y Recall de la clase favorita. ROC-AUC mide capacidad de ordenación.
- Los algoritmos son Regresión Logística, Random Forest y SVM-RBF.
- Todo preprocesamiento aprendible (imputación, escalado, vocabulario de géneros) ocurre dentro de cada fold.
- Esta base son tus álbumes seleccionados/calificados, por lo que los resultados describen esa selección y no todos los álbumes del mundo.
- Las variables musicales de Spotify están agregadas por álbum. La evaluación aleatoria estratificada podría ser optimista con artistas repetidos; una evaluación adicional por artista sería recomendable si la finalidad es predecir artistas desconocidos.
- El conjunto test no debe utilizarse para reajustar el modelo después de revisar las métricas.
- No se necesita Docker, Airflow, FastAPI, cuenta de MLflow ni servicios de nube.

## Solución de problemas

- **`No module named mlflow`:** instalar con el Python de `.venv` exactamente como en el paso 1.
- **`Connection refused` o error HTTP:** mantener servidor abierto en terminal 1 y comprobar `http://127.0.0.1:5000`.
- **Puerto 5000 ocupado:** cerrar procesos previos de MLflow o usar otro puerto, configurando el argumento `--tracking-uri` de los scripts.
- **No aparece el modelo en Registry:** ejecutar `src.register_champion` después de `src.train` sin `--sin-mlflow`.
- **Errores de entorno:** ejecutar siempre desde la carpeta raíz del proyecto para encontrar `src` y `data`.

## Referencias técnicas

- https://mlflow.org/docs/latest/ml/tracking/
- https://mlflow.org/docs/latest/ml/model-registry/
- https://mlflow.org/docs/latest/self-hosting/
