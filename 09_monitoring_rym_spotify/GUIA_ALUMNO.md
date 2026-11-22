# Guía de actividades — Práctica 9: Monitoreo con Evidently AI

**Proyecto:** RYM + Spotify, clasificación de favoritos (puntuación RYM de 9 a 10).  **Duración estimada para clase:** 2 horas.

## Objetivos de aprendizaje

- Preparar una referencia de las mismas entradas que utiliza FastAPI.
- Ingerir registros JSONL de inferencia y verificar su calidad.
- Distinguir **data drift** de **degradación de métricas de clasificación**.
- Ejecutar Evidently para generar un reporte HTML y resultados JSON.
- Repetir la ejecución en Docker y documentar reproducibilidad.

## Secuencia sugerida

| Tiempo | Actividad | Evidencia |
|---|---|---|
| 0–15 min | Descomprimir y crear `.venv`, instalar requisitos | captura de instalación |
| 15–30 min | Ejecutar `monitoring.preparar_datos` y tests | baseline de 611 álbumes y pytest |
| 30–50 min | Generar `demo_similar.jsonl` y reporte Evidently | HTML sin modificaciones forzadas |
| 50–70 min | Generar `demo_cambio.jsonl` y segundo reporte | comparación de drift por columna |
| 70–90 min | Importar `predicciones.jsonl` o enviar consultas API etiquetadas como pruebas | reporte de entradas y predicciones |
| 90–110 min | Ejecutar con Docker / Fedora | reporte producido por contenedor |
| 110–120 min | Redactar conclusiones y anexar capturas | conclusiones MLOps |

## Comandos esenciales — Windows

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m monitoring.preparar_datos
.\.venv\Scripts\python.exe -m monitoring.generar_demo --escenario similar --salida data/demo_similar.jsonl
.\.venv\Scripts\python.exe -m monitoring.generar_reporte --log data/demo_similar.jsonl
# Guardar copia de reports/ antes de la siguiente ejecución.
.\.venv\Scripts\python.exe -m monitoring.generar_demo --escenario cambio --salida data/demo_cambio.jsonl
.\.venv\Scripts\python.exe -m monitoring.generar_reporte --log data/demo_cambio.jsonl
Start-Process .\reports\drift_rym_spotify.html
```

## Comandos esenciales — Docker

```powershell
docker compose build
docker compose run --rm monitor python -m monitoring.generar_reporte --log data/demo_cambio.jsonl
```

Al ejecutar el monitoreo en Fedora con SELinux, incluir el override `-f compose.yaml -f compose.fedora.yaml` (ver `README.md`).

## Preguntas para la entrega

1. ¿Cuántos álbumes existen en el CSV inicial y cuántos son válidos para el baseline?
2. ¿Qué características presentan cambios entre `similar` y `cambio`? ¿Qué decisiones de Evidently se observan en el HTML?
3. ¿Qué distingue una solicitud sintética de una respuesta calculada realmente por el Champion?
4. ¿Por qué no puede calcularse F1 de producción sin nuevas puntuaciones RYM verificadas?
5. ¿Qué se haría si cambia la distribución de `promedio_energy` o `anio_spotify` en consultas reales?
6. ¿Cómo evita Docker depender de la instalación local de Evidently en Windows/Fedora?

**Entrega mínima:** 2 capturas de reportes de escenarios distintos, pruebas, ejecución Docker y un documento breve con los hallazgos y las precauciones de interpretar una simulación.
