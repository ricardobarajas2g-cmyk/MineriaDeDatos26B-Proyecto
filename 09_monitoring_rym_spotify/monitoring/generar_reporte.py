"""Reporte offline de data drift Evidently 0.7.19 para RYM + Spotify."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config import (DATA_REFERENCIA, FEATURES_MONITOREO, GENERO_PRINCIPAL,
                     LOG_PREDETERMINADO, NUMERICAS, REPORTS_DIR)
from .datos import estadisticas_predicciones, leer_logs_jsonl, leer_referencia


def extraer_resumen_evidently(data):
    """Campos opcionales según serialización Evidently. El JSON completo se guarda intacto."""
    resultado = {'columnas_con_drift': None, 'fraccion_columnas_con_drift': None,
                 'detalle_por_columna': {}}
    for metric in data.get('metrics', []):
        if not isinstance(metric, dict):
            continue
        nombre = str(metric.get('metric_name') or metric.get('metric') or '')
        valor = metric.get('value')
        config = metric.get('config') or {}
        if 'DriftedColumnsCount' in nombre and isinstance(valor, dict):
            resultado['columnas_con_drift'] = valor.get('count')
            resultado['fraccion_columnas_con_drift'] = valor.get('share')
        elif 'ValueDrift' in nombre:
            col = config.get('column')
            if col and valor is not None:
                resultado['detalle_por_columna'][str(col)] = {'valor_metrica': valor}
    return resultado


def reportar(referencia=DATA_REFERENCIA, log=LOG_PREDETERMINADO, salida=REPORTS_DIR,
             minimo=10, permitir_demo=True):
    referencia = leer_referencia(referencia)
    actual, calidad = leer_logs_jsonl(log)
    if len(actual) < minimo:
        raise ValueError(f'Solo hay {len(actual)} solicitudes válidas (mínimo {minimo}). '
                         f'Generar una demo de 120 filas o acumular consultas reales en FastAPI.')
    if not permitir_demo and actual['origen'].isin(['demo_sintetica', 'simulacion_api']).any():
        raise ValueError('El archivo contiene solicitudes de prueba; use logs reales o quite --solo-reales')

    # Importación diferida: tests de ingesta pueden correr sin instalar Evidently.
    try:
        from evidently import Dataset, DataDefinition, Report
        from evidently.presets import DataDriftPreset
    except ImportError as err:
        raise RuntimeError('Falta Evidently. Instalar con: python -m pip install -r requirements.txt') from err

    definition = DataDefinition(numerical_columns=NUMERICAS,
                                categorical_columns=[GENERO_PRINCIPAL])
    ref_dataset = Dataset.from_pandas(referencia[FEATURES_MONITOREO], data_definition=definition)
    cur_dataset = Dataset.from_pandas(actual[FEATURES_MONITOREO], data_definition=definition)
    report = Report([DataDriftPreset(columns=FEATURES_MONITOREO)])
    snapshot = report.run(cur_dataset, ref_dataset)

    destino = Path(salida)
    destino.mkdir(parents=True, exist_ok=True)
    html = destino / 'drift_rym_spotify.html'
    json_path = destino / 'drift_evidently.json'
    snapshot.save_html(str(html))
    snapshot.save_json(str(json_path))
    structured = snapshot.dict()

    stats = estadisticas_predicciones(actual)
    timestamps = pd.to_datetime(actual['timestamp_utc'], errors='coerce', utc=True)
    demo = bool(actual['origen'].isin(['demo_sintetica', 'simulacion_api']).any())
    cambios = extraer_resumen_evidently(structured)
    medias = {}
    for c in NUMERICAS:
        medias[c] = {'referencia': round(float(referencia[c].mean()), 4),
                    'actual': round(float(actual[c].mean()), 4)}
    resumen = {
        'generado_utc': datetime.now(timezone.utc).isoformat(),
        'referencia_filas': int(len(referencia)),
        'actual_filas': int(len(actual)),
        'solicitudes_sinteticas': demo,
        'origen_log': str(log),
        'periodo_utc': {
            'inicio': timestamps.min().isoformat() if timestamps.notna().any() else None,
            'fin': timestamps.max().isoformat() if timestamps.notna().any() else None,
        },
        'calidad_ingesta': calidad,
        'medias_entradas': medias,
        'predicciones_recientes': stats,
        'resultados_evidently': cambios,
        'interpretacion': 'Las métricas describen drift de entradas; sin nuevas calificaciones RYM no es posible evaluar F1, exactitud ni caída de rendimiento.',
        'advertencia_muestra': ('Menos de 30 solicitudes: resultados estadísticos poco estables.'
                                if len(actual) < 30 else None),
        'advertencia_demostracion': ('Se utilizaron solicitudes de demostración (generadas o enviadas a la API).' if demo else None),
    }
    json_resumen = destino / 'resumen_monitoreo.json'
    json_resumen.write_text(json.dumps(resumen, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    lineas = [
        '# Monitoreo RYM + Spotify', '',
        f'- Observaciones históricas de referencia: **{len(referencia)}**',
        f'- Solicitudes recientes analizables: **{len(actual)}**',
        f'- Archivo analizado: `{Path(log).name}`',
        f'- ¿Datos de demostración?: **{"Sí" if demo else "No declarado"}**',
        f'- Predicciones con clase disponible: **{stats["predicciones_validas"]}**',
        f'- Favoritos predichos (cuando existen clases): **{stats["porcentaje_predichos_favoritos"]}%**' if stats['predicciones_validas'] else '- Clases: **no disponibles (demo sin modelo)**',
        '', '## Medias por característica', '',
        '| Variable | Referencia | Reciente |', '|---|---:|---:|',
    ]
    for k, v in medias.items():
        lineas.append(f'| `{k}` | {v["referencia"]} | {v["actual"]} |')
    lineas += ['', '## Reporte Evidently', '',
               '- Abrir `drift_rym_spotify.html` y consultar el detalle de la detección por columna.',
               '- Consultar `drift_evidently.json` para los resultados sin procesar.',
               '- El resumen estadístico es descriptivo; las decisiones de drift proceden de Evidently.',
               '- Sin etiquetas RYM nuevas no puede calcularse F1 de producción.', '']
    if demo:
        lineas += ['**Atención:** este escenario usa solicitudes sintéticas, útil solamente para demostrar drift.', '']
    if len(actual) < 30:
        lineas += ['**Atención:** muestra pequeña; interpretar con cautela.', '']
    (destino / 'resumen_monitoreo.md').write_text('\n'.join(lineas), encoding='utf-8')
    return resumen, html


def main():
    parser = argparse.ArgumentParser(description='Ejecutar Evidently 0.7.x con referencia RYM y logs FastAPI')
    parser.add_argument('--referencia', type=Path, default=DATA_REFERENCIA)
    parser.add_argument('--log', type=Path, default=LOG_PREDETERMINADO)
    parser.add_argument('--salida', type=Path, default=REPORTS_DIR)
    parser.add_argument('--minimo', type=int, default=10)
    parser.add_argument('--solo-reales', action='store_true', help='Rechaza logs con origen demo_sintetica')
    args = parser.parse_args()
    try:
        resumen, archivo = reportar(args.referencia, args.log, args.salida,
                                    minimo=max(1, args.minimo), permitir_demo=not args.solo_reales)
    except (FileNotFoundError, ValueError, RuntimeError) as err:
        parser.exit(2, f'No pudo generarse el reporte: {err}\n')
    print(f'Referencia: {resumen["referencia_filas"]}; actuales: {resumen["actual_filas"]}')
    print(f'Reporte HTML Evidently: {archivo}')
    print(f'Resumen: {args.salida / "resumen_monitoreo.md"}')
    if resumen['solicitudes_sinteticas']:
        print('IMPORTANTE: los registros incluyen solicitudes de demostración o pruebas enviadas a la API.')


if __name__ == '__main__':
    main()
