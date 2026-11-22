# Guía de actividades del alumno — 120 minutos

**Objetivo:** comparar modelos en MLflow y registrar el Champion, sin reprogramar algoritmos.

| Minutos | Tarea | Evidencia |
|---|---|---|
| 0–15 | Abrir proyecto, confirmar archivos y entender variable `favorito_9_10` | CSV abierto |
| 15–30 | Crear entorno e instalar paquetes; ejecutar `python -m pytest -q` y `python -m src.prepare_data` | Recuento 611 |
| 30–45 | Iniciar servidor MLflow (terminal 1), abrir navegador | Página de experimentos |
| 45–70 | Ejecutar `python -m src.train` en terminal 2 | Tres runs |
| 70–90 | Comparar CV F1, ROC-AUC y gráficas; explicar diferencias entre 3 modelos | Tabla de métricas |
| 90–105 | Ejecutar `python -m src.register_champion` | Modelo registrado y alias |
| 105–115 | Ejecutar `python -m src.verify_champion` | Inferencia desde Registry |
| 115–120 | Guardar capturas y redactar conclusión | Entregable |

**Preguntas para el reporte:**
1. ¿Cuál tuvo mayor `cv_f1_mean`? ¿Por qué ese criterio se escogió para decidir el Champion?
2. ¿Coincide el ganador por `cv_f1_mean` con el ganador por `test_roc_auc`? ¿Qué significa si no coinciden?
3. ¿Para qué sirve el Model Registry?
4. ¿Por qué se excluye `rating_rym` de las variables predictoras?
5. ¿Por qué el vocabulario de géneros debe aprenderse dentro de los folds de entrenamiento?

**Experimento opcional:** modifica `C` de SVM en `src/models.py`, ejecuta de nuevo los tres runs y compara. Evita elegir parámetros basándote en test; usa los resultados de CV.
