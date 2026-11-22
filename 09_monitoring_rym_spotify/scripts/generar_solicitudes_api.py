"""Prueba controlada: envía solicitudes de práctica a POST /predict; respuestas reales del Champion.

Al registrar artista='[SIMULACION API]' se distingue tráfico generado del genuino.
NO ejecutar contra servicios ajenos ni usar como tráfico de producción.
"""
import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

from monitoring.config import DATA_ORIGINAL, GENERO, NUMERICAS
from monitoring.datos import referencia_desde_original


def main():
    parser = argparse.ArgumentParser(description='Enviar consultas de prueba a FastAPI local')
    parser.add_argument('--url', default='http://127.0.0.1:8001')
    parser.add_argument('--cantidad', type=int, default=30)
    parser.add_argument('--escenario', choices=['similar','cambio'], default='similar')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if not 1 <= args.cantidad <= 500:
        parser.error('--cantidad debe estar entre 1 y 500')
    if not args.url.startswith(('http://localhost:', 'http://127.0.0.1:', 'http://[::1]:')):
        parser.error('Por seguridad el script solo envía consultas a localhost/127.0.0.1')
    df = pd.read_csv(DATA_ORIGINAL)
    _, info = referencia_desde_original(DATA_ORIGINAL)
    ratings = pd.to_numeric(df['rating_rym'], errors='coerce')
    labels = pd.to_numeric(df['favorito_9_10'], errors='coerce')
    df = df.loc[ratings.between(1,10) & labels.eq((ratings >= 9).astype(int))].reset_index(drop=True)
    rng = np.random.default_rng(args.seed)
    enviados = 0
    for idx in range(args.cantidad):
        item = df.iloc[int(rng.integers(len(df)))]
        entrada = {c: float(item[c]) for c in NUMERICAS}
        entrada['anio_spotify'] = int(item['anio_spotify'])
        if args.escenario == 'cambio':
            entrada['promedio_energy'] = float(rng.uniform(.87,.99))
            entrada['promedio_acousticness'] = float(rng.uniform(.001,.04))
            entrada['anio_spotify'] = int(rng.integers(2020, 2026))
        entrada[GENERO] = str(item[GENERO])
        entrada['artista'] = '[SIMULACION API]'
        entrada['album'] = f'Consulta {idx + 1} ({args.escenario})'
        request = Request(args.url.rstrip('/') + '/predict',
                          data=json.dumps(entrada).encode('utf-8'),
                          headers={'Content-Type':'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.load(response)
                enviados += 1
                print(f'{idx+1}/{args.cantidad} | clase={payload.get("prediction")} | p={payload.get("probabilidad_favorito")}')
        except (HTTPError, URLError, TimeoutError) as err:
            parser.exit(2, f'Error en POST /predict ({idx+1}/{args.cantidad}): {err}\n')
    print(f'Enviadas {enviados} consultas SIMULADAS. FastAPI las registra con marcador [SIMULACION API].')
    print('Copiar logs del contenedor mientras sigue ejecutándose; ver README.md.')


if __name__ == '__main__':
    main()
