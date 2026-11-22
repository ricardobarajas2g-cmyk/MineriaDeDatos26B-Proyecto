# Notas para el docente — Práctica 9 RYM + Spotify

Los archivos se entregan listos para uso en Windows y Fedora (Docker). Evidently: API 0.7.19 fijada en requirements.txt.

- Dataset original de la alumna/alumno: 618 registros, 23 columnas. Filtrar rating válido = 611. Los 7 sin rating se excluyen.
- Variables monitoreadas: nueve medias numéricas de Spotify y `genero_principal`, extraído de la cadena de géneros separada por `|`.
- La referencia histórica usa los 611 registros calificados. El entrenamiento original utilizó 488; no afirmar equivalencia con el train exacto.
- Los 120 registros incluidos en `data/demo_predicciones.jsonl` son sintéticos (escenario `cambio`), con response vacío para no falsificar inferencias.
- Los registros reales de inferencia se obtienen de `logs/predicciones.jsonl` de Prácticas 6–8 o se generan llamadas API de prueba con el marcador `[SIMULACION API]`.
- Evidently produce HTML y JSON, más resumen local de entradas, calidad y clases/probabilidades (solo cuando existen).
- El repo ignora CSV, JSONL y resultados. La imagen de Docker contiene solo código y requirements; los datos se montan por volumen.
- Las 19 pruebas de ingesta y orquestación con sustituto de Evidently se pueden ejecutar sin dependencias de MLflow. La prueba del reporte real exige instalar Evidently y ejecutarlo en Windows o Docker.

**Evaluación sugerida:** entradas históricas/recentes correctas (25%), ejecución y explicación de Evidently (35%), Docker y reproducibilidad (20%), interpretación ética y técnica de reportes (20%).
