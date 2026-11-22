# Notas de verificación docente

- Base: 618 filas, 611 etiquetadas, clase favorita definida como rating >=9.
- Pipeline copiado de Práctica 4: `ColumnTransformer`, `SimpleImputer`, `StandardScaler`, `CountVectorizer(token_pattern=r"[^|]+")`, `LogisticRegression(C=1, max_iter=1500, random_state=42)`.
- Modelo incluido: réplica local entrenada en las mismas 80% filas de entrenamiento. **No pretende ser la versión remota real registrada en la máquina del alumno**. El exportador opcional conecta con MLflow para reutilizar su Champion.
- El ZIP intencionalmente evita Docker, Airflow y MLflow como dependencias para centrarse en FastAPI.
- El listado `/albums` contiene ejemplos sin rating ni etiqueta para no revelar `target` como variable de entrada.
- Logs JSONL son útiles para la práctica futura de Evidently; solicitar únicamente datos anónimos y no subirlos a repositorios públicos.
- Comparaciones cambiando energía son contrafactuales exploratorios, no pruebas de causalidad.
- Para comprobar: `.venv\Scripts\python.exe -m pytest -v` y abrir `/docs`.
