"""Genera un baseline histórico local a partir del CSV RYM+Spotify."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_ORIGINAL, DATA_REFERENCIA, FEATURES_MONITOREO
from .datos import referencia_desde_original


def preparar(csv=DATA_ORIGINAL, salida=DATA_REFERENCIA):
    csv, salida = Path(csv), Path(salida)
    df, meta = referencia_desde_original(csv)
    if len(df) < 10:
        raise ValueError('Muy pocos registros históricos válidos para monitoreo')
    salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida, index=False, encoding='utf-8')
    info = {
        **meta,
        'generado_utc': datetime.now(timezone.utc).isoformat(),
        'sha256_csv_original': hashlib.sha256(csv.read_bytes()).hexdigest(),
        'columnas_analizadas': FEATURES_MONITOREO,
        'procedencia': 'álbumes calificados (1-10) de RYM+Spotify, SIN rating/target; referencia histórica de 611, no necesariamente el train exacto de 488',
        'nota_generos': 'género_principal: primer género separado por |; solo para comparación de categorías, el modelo real usa cadena completa de géneros',
    }
    (salida.parent / 'referencia_info.json').write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding='utf-8')
    return info


def main():
    parser = argparse.ArgumentParser(description='Preparar datos históricos de RYM + Spotify para Evidently')
    parser.add_argument('--csv', type=Path, default=DATA_ORIGINAL)
    parser.add_argument('--salida', type=Path, default=DATA_REFERENCIA)
    args = parser.parse_args()
    info = preparar(args.csv, args.salida)
    print(json.dumps(info, indent=2, ensure_ascii=False))
    print(f'Referencia preparada: {args.salida}')


if __name__ == '__main__':
    main()
