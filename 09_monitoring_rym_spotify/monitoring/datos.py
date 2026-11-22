"""Extracción y controles de calidad para referencia y logs de inferencia."""
import json
from pathlib import Path

import pandas as pd

from .config import (FEATURES_MONITOREO, GENERO, GENERO_PRINCIPAL, NUMERICAS,
                     RANGOS)


def genero_principal(value):
    """Proyección categórica del primer género en una cadena separada por |."""
    if value is None or pd.isna(value):
        return 'desconocido'
    primero = str(value).split('|', 1)[0].strip().lower()
    return ' '.join(primero.split()) or 'desconocido'


def transformar_features(df):
    """Valida los rangos originales sin imputar ni fabricar datos."""
    requeridas = NUMERICAS + [GENERO]
    faltan = sorted(set(requeridas) - set(df.columns))
    if faltan:
        raise ValueError(f'Faltan características requeridas: {faltan}')
    data = df.copy()
    for columna in NUMERICAS:
        data[columna] = pd.to_numeric(data[columna], errors='coerce')
    data[GENERO_PRINCIPAL] = data[GENERO].map(genero_principal)
    valida = pd.Series(True, index=data.index)
    for columna, (minimo, maximo) in RANGOS.items():
        valida &= data[columna].between(minimo, maximo)
    valida &= data[GENERO].notna() & data[GENERO].astype(str).str.strip().ne('')
    resultado = data.loc[valida, FEATURES_MONITOREO].copy().reset_index(drop=True)
    return resultado, int((~valida).sum())


def referencia_desde_original(path):
    """Usa álbumes puntuados 1-10 con etiqueta coherente; evita columnas objetivo."""
    ruta = Path(path)
    if not ruta.exists():
        raise FileNotFoundError(f'CSV original ausente: {ruta}')
    df = pd.read_csv(ruta)
    for campo in ('rating_rym', 'favorito_9_10'):
        if campo not in df.columns:
            raise ValueError(f'El CSV debe contener {campo}')
    ratings = pd.to_numeric(df['rating_rym'], errors='coerce')
    targets = pd.to_numeric(df['favorito_9_10'], errors='coerce')
    validos = ratings.between(1, 10) & targets.isin([0, 1]) & targets.eq((ratings >= 9).astype(int))
    base = df.loc[validos].copy()
    resultado, invalidas = transformar_features(base)
    return resultado, {'filas_originales': int(len(df)),
                       'filas_con_rating_valido': int(validos.sum()),
                       'filas_descartadas_por_calidad': invalidas,
                       'filas_referencia': int(len(resultado))}


def leer_referencia(path):
    """Lee el archivo generado; no requiere scikit-learn ni el modelo Champion."""
    ruta = Path(path)
    if not ruta.is_file():
        raise FileNotFoundError(f'No se encontró referencia {ruta}. Ejecutar python -m monitoring.preparar_datos')
    df = pd.read_csv(ruta)
    faltan = sorted(set(FEATURES_MONITOREO) - set(df.columns))
    if faltan:
        raise ValueError(f'Faltan columnas en referencia: {faltan}')
    for c in NUMERICAS:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    data = df[FEATURES_MONITOREO].copy()
    data[GENERO_PRINCIPAL] = data[GENERO_PRINCIPAL].fillna('desconocido').astype(str)
    valido = data[NUMERICAS].notna().all(axis=1)
    for col, (low, high) in RANGOS.items():
        valido &= data[col].between(low, high)
    if not valido.all():
        raise ValueError('La referencia contiene características ausentes o fuera de rango; regenerar referencia')
    if len(data) < 10:
        raise ValueError('La referencia tiene menos de 10 álbumes')
    return data


def leer_logs_jsonl(path):
    """Extrae solicitudes auténticas del formato de app/main.py; ignora líneas malformadas.

    Retorna todas las solicitudes validables, sus respuestas opcionales y conteos de calidad.
    No asume que todas las solicitudes son tráfico real (puede haber pruebas).
    """
    ruta = Path(path)
    if not ruta.exists():
        raise FileNotFoundError(f'Logs no encontrados: {ruta}. Copiar desde FastAPI o generar demo.')
    registros = []
    errores = []
    vistos = set()
    duplicados = 0
    total = 0
    with ruta.open('r', encoding='utf-8-sig') as f:
        for num, raw in enumerate(f, 1):
            if not raw.strip():
                continue
            total += 1
            try:
                obj = json.loads(raw)
                if not isinstance(obj, dict) or not isinstance(obj.get('request'), dict):
                    raise ValueError('registro sin objeto request')
                ident = obj.get('id')
                if ident is not None and ident in vistos:
                    duplicados += 1
                    continue
                pedido = obj['request']
                faltan = sorted(set(NUMERICAS + [GENERO]) - pedido.keys())
                if faltan:
                    raise ValueError(f'faltan características: {faltan}')
                row = {c: pedido[c] for c in NUMERICAS + [GENERO]}
                response = obj.get('response') or {}
                if not isinstance(response, dict):
                    response = {}
                row['prediction'] = response.get('prediction')
                row['probabilidad_favorito'] = response.get('probabilidad_favorito')
                row['timestamp_utc'] = obj.get('timestamp_utc')
                row['modelo'] = response.get('modelo')
                row['origen'] = obj.get('origen') or ('simulacion_api' if str(pedido.get('artista', '')).startswith('[SIMULACION API]') else 'log_fastapi')
                registros.append(row)
                if ident is not None:
                    vistos.add(ident)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as err:
                errores.append({'linea': num, 'motivo': str(err)[:180]})

    if not registros:
        raise ValueError(f'No hay solicitudes procesables en {ruta} ({len(errores)} líneas erróneas).')
    df = pd.DataFrame(registros)
    filtrado, descartadas = transformar_features(df)
    # Los índices del filtrado se reinician, de modo que los datos de respuesta se
    # vuelven a alinear calculando las filas válidas en paralelo sin perder su orden.
    # Se evita depender del índice de origen del JSONL.
    with_meta = df.copy()
    for c in NUMERICAS:
        with_meta[c] = pd.to_numeric(with_meta[c], errors='coerce')
    valido = pd.Series(True, index=with_meta.index)
    for col, (a, b) in RANGOS.items():
        valido &= with_meta[col].between(a, b)
    valido &= with_meta[GENERO].notna() & with_meta[GENERO].astype(str).str.strip().ne('')
    extras = with_meta.loc[valido, ['prediction', 'probabilidad_favorito', 'timestamp_utc', 'modelo', 'origen']].reset_index(drop=True)
    resultado = pd.concat([filtrado, extras], axis=1)
    if resultado.empty:
        raise ValueError('No hay solicitudes con datos válidos dentro de los rangos de FastAPI.')
    calidad = {'lineas_no_vacias': total, 'registros_con_request': len(registros),
               'ids_duplicados': duplicados, 'lineas_incorrectas': len(errores),
               'solicitudes_fuera_de_rango': descartadas,
               'solicitudes_analizables': int(len(resultado)),
               'errores_muestra': errores[:5]}
    return resultado, calidad


def estadisticas_predicciones(df):
    """Estadística descriptiva: no requiere ground truth ni asume calibración."""
    p = pd.to_numeric(df.get('prediction', pd.Series(dtype=float)), errors='coerce')
    proba = pd.to_numeric(df.get('probabilidad_favorito', pd.Series(dtype=float)), errors='coerce')
    p = p[p.isin([0, 1])]
    proba = proba[proba.between(0, 1)]
    return {
        'predicciones_validas': int(len(p)),
        'porcentaje_predichos_favoritos': round(100 * float(p.mean()), 2) if len(p) else None,
        'probabilidades_validas': int(len(proba)),
        'probabilidad_media': round(float(proba.mean()), 4) if len(proba) else None,
        'probabilidad_mediana': round(float(proba.median()), 4) if len(proba) else None,
        'distribucion_predicciones': {str(k): int((p == k).sum()) for k in (0, 1)},
        'origenes': {str(k): int(v) for k, v in df['origen'].value_counts().items()} if 'origen' in df else {},
    }
