import json
from pathlib import Path

import pandas as pd
import pytest

from monitoring.config import DATA_ORIGINAL, FEATURES_MONITOREO, NUMERICAS
from monitoring.datos import (estadisticas_predicciones, genero_principal,
                              leer_logs_jsonl, leer_referencia,
                              referencia_desde_original, transformar_features)
from monitoring.generar_demo import generar_demo
from monitoring.preparar_datos import preparar


def fila():
    return {'promedio_danceability': .35, 'promedio_energy': .7,
            'promedio_acousticness': .2, 'promedio_instrumentalness': .8,
            'promedio_valence': .45, 'promedio_tempo': 112,
            'promedio_popularity': 38, 'promedio_loudness': -12,
            'anio_spotify': 2017, 'generos_frecuentes': 'idm | ambient'}


def test_esquema_de_columnas_esperadas():
    assert len(NUMERICAS) == 9
    assert len(FEATURES_MONITOREO) == 10
    assert 'rating_rym' not in FEATURES_MONITOREO


def test_genero_principal_canonico():
    assert genero_principal('  IDM  |  Ambient  ') == 'idm'
    assert genero_principal(None) == 'desconocido'
    assert genero_principal(' | ') == 'desconocido'


def test_transformar_entradas_validas():
    x, invalidas = transformar_features(pd.DataFrame([fila()]))
    assert invalidas == 0
    assert x['genero_principal'].iloc[0] == 'idm'
    assert list(x.columns) == FEATURES_MONITOREO


def test_transformar_descarta_fuera_de_rango():
    entrada = fila()
    entrada['promedio_energy'] = 1.1
    x, invalidas = transformar_features(pd.DataFrame([fila(), entrada]))
    assert invalidas == 1 and len(x) == 1


def test_referencia_rym_filtra_siete_no_calificados():
    base, info = referencia_desde_original(DATA_ORIGINAL)
    assert info['filas_originales'] == 618
    assert info['filas_con_rating_valido'] == 611
    assert len(base) == 611
    assert not base.isna().any().any()


def test_preparar_referencia_y_releer(tmp_path):
    salida = tmp_path / 'referencia.csv'
    info = preparar(DATA_ORIGINAL, salida)
    assert info['filas_referencia'] == 611
    assert (tmp_path / 'referencia_info.json').is_file()
    base = leer_referencia(salida)
    assert list(base.columns) == FEATURES_MONITOREO


def test_log_real_extrae_respuesta(tmp_path):
    evento = {'id':'z1', 'request':fila(),
              'response':{'prediction':1,'probabilidad_favorito':.723,'modelo':'logistic'},
              'timestamp_utc':'2026-11-22T00:00:00+00:00'}
    ruta = tmp_path / 'registro.jsonl'
    ruta.write_text(json.dumps(evento, ensure_ascii=False) + '\n', encoding='utf-8')
    data, calidad = leer_logs_jsonl(ruta)
    assert len(data) == 1 and calidad['solicitudes_analizables'] == 1
    assert data.iloc[0]['genero_principal'] == 'idm'
    stats = estadisticas_predicciones(data)
    assert stats['porcentaje_predichos_favoritos'] == 100
    assert stats['probabilidad_media'] == .723


def test_logs_duplicados_y_malformados(tmp_path):
    evento = {'id':'id1','request':fila(), 'response':{}}
    ruta = tmp_path / 'registros.jsonl'
    ruta.write_text(json.dumps(evento) + '\n' + json.dumps(evento) + '\n' + '{broken}\n', encoding='utf-8')
    data, calidad = leer_logs_jsonl(ruta)
    assert len(data) == 1
    assert calidad['ids_duplicados'] == 1
    assert calidad['lineas_incorrectas'] == 1


def test_log_invalido_descarta_filas_fuera_de_rango(tmp_path):
    invalida = fila()
    invalida['promedio_tempo'] = -2
    ruta = tmp_path / 'logs.jsonl'
    evento = {'request':fila(), 'response':{}}
    evento2 = {'request':invalida,'response':{}}
    ruta.write_text(json.dumps(evento)+'\n'+json.dumps(evento2)+'\n', encoding='utf-8')
    data, calidad = leer_logs_jsonl(ruta)
    assert len(data) == 1
    assert calidad['solicitudes_fuera_de_rango'] == 1


def test_demo_sintetico_no_fabrica_respuestas(tmp_path):
    salida = generar_demo(salida=tmp_path / 'demo.jsonl', cantidad=40, escenario='cambio')
    data, calidad = leer_logs_jsonl(salida)
    assert len(data) == 40
    assert calidad['solicitudes_analizables'] == 40
    assert data['origen'].eq('demo_sintetica').all()
    assert data['prediction'].isna().all()
    assert (data['promedio_energy'] > .86).all()


def test_muestra_similar_sin_cambios_forzados(tmp_path):
    salida = generar_demo(salida=tmp_path / 'similar.jsonl', cantidad=25, escenario='similar')
    data, _ = leer_logs_jsonl(salida)
    assert len(data) == 25
    assert data['probabilidad_favorito'].isna().all()


def test_referencia_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        leer_referencia(tmp_path / 'no_existe.csv')


def test_log_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        leer_logs_jsonl(tmp_path / 'no_existe.jsonl')


def test_log_sin_request_da_error(tmp_path):
    ruta = tmp_path / 'invalido.jsonl'
    ruta.write_text('{"hello":"world"}\n', encoding='utf-8')
    with pytest.raises(ValueError, match='No hay solicitudes procesables'):
        leer_logs_jsonl(ruta)


def test_identifica_solicitudes_de_api_simuladas(tmp_path):
    pedido = fila()
    pedido['artista'] = '[SIMULACION API]'
    ruta = tmp_path / 'log.jsonl'
    ruta.write_text(json.dumps({'request': pedido, 'response': {'prediction':0}}), encoding='utf-8')
    data, _ = leer_logs_jsonl(ruta)
    assert data['origen'].iloc[0] == 'simulacion_api'
