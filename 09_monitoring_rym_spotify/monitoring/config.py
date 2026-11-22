"""Contrato de datos compatible con POST /predict de las Prácticas 6-8."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_ORIGINAL = ROOT / 'data' / 'rym_spotify_con_generos.csv'
DATA_REFERENCIA = ROOT / 'data' / 'referencia_rym_spotify.csv'
LOG_PREDETERMINADO = ROOT / 'logs' / 'predicciones.jsonl'
REPORTS_DIR = ROOT / 'reports'
NUMERICAS = [
    'promedio_danceability', 'promedio_energy', 'promedio_acousticness',
    'promedio_instrumentalness', 'promedio_valence', 'promedio_tempo',
    'promedio_popularity', 'promedio_loudness', 'anio_spotify',
]
GENERO = 'generos_frecuentes'
GENERO_PRINCIPAL = 'genero_principal'
FEATURES_MONITOREO = NUMERICAS + [GENERO_PRINCIPAL]
# Reglas consistentes con el contrato Pydantic de app/schemas.py de Práctica 8.
RANGOS = {
    'promedio_danceability': (0, 1),
    'promedio_energy': (0, 1),
    'promedio_acousticness': (0, 1),
    'promedio_instrumentalness': (0, 1),
    'promedio_valence': (0, 1),
    'promedio_tempo': (0, 300),
    'promedio_popularity': (0, 100),
    'promedio_loudness': (-80, 15),
    'anio_spotify': (1900, 2100),
}
