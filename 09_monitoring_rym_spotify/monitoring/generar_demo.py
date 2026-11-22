"""Solicitudes SINTÉTICAS para aprender a utilizar Evidently, sin inferencias reales."""
import argparse
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DATA_ORIGINAL, NUMERICAS, GENERO
from .datos import referencia_desde_original


def generar_demo(csv=DATA_ORIGINAL, salida=None, cantidad=120, escenario='cambio', seed=42):
    if cantidad < 10:
        raise ValueError('cantidad debe ser al menos 10')
    if escenario not in ('similar', 'cambio'):
        raise ValueError('escenario debe ser similar o cambio')
    ruta = Path(salida) if salida else Path(csv).parent / 'demo_predicciones.jsonl'
    # Reutilizar las distribuciones válidas de la referencia, NO las calificaciones.
    referencia, _ = referencia_desde_original(csv)
    rng = np.random.default_rng(seed)
    muestra = referencia.iloc[rng.choice(len(referencia), size=cantidad, replace=True)].copy()
    if escenario == 'cambio':
        # Señal de drift deliberada en varias variables para la actividad guiada.
        muestra['promedio_energy'] = rng.uniform(0.87, 0.99, size=cantidad)
        muestra['promedio_acousticness'] = rng.uniform(0.001, 0.04, size=cantidad)
        muestra['anio_spotify'] = rng.integers(2020, 2026, size=cantidad)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ahora = datetime.now(timezone.utc)
    with ruta.open('w', encoding='utf-8') as f:
        for idx, (_, fila) in enumerate(muestra.iterrows()):
            pedido = {c: float(fila[c]) for c in NUMERICAS}
            pedido['anio_spotify'] = int(fila['anio_spotify'])
            pedido[GENERO] = str(fila['genero_principal'])
            pedido['artista'] = 'DEMO (sin identidad real)'
            pedido['album'] = f'Album simulado {idx+1}'
            evento = {
                'id': str(uuid.uuid5(uuid.NAMESPACE_DNS, f'rym-monitor-demo-{seed}-{escenario}-{idx}')),
                'timestamp_utc': (ahora - timedelta(minutes=cantidad - idx)).isoformat(),
                'request': pedido,
                # No hay respuesta de modelo: no fabricar probabilidades/predicciones.
                'response': {},
                'origen': 'demo_sintetica',
            }
            f.write(json.dumps(evento, ensure_ascii=False) + '\n')
    return ruta


def main():
    parser = argparse.ArgumentParser(description='Crear logs sintéticos identificados, sin ejecutar el Champion')
    parser.add_argument('--csv', type=Path, default=DATA_ORIGINAL)
    parser.add_argument('--salida', type=Path, default=None)
    parser.add_argument('--cantidad', type=int, default=120)
    parser.add_argument('--escenario', choices=['similar', 'cambio'], default='cambio')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    ruta = generar_demo(args.csv, args.salida, args.cantidad, args.escenario, args.seed)
    print(f'GENERACIÓN SINTÉTICA ({args.escenario}): {ruta}')
    print('Los campos response están vacíos: son entradas de demostración, no predicciones reales.')


if __name__ == '__main__':
    main()
