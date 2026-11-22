"""Sustituir artefacto local por el Champion real de una práctica anterior.

Requiere MLflow instalado en el entorno y servidor local en marcha.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import joblib
import pandas as pd
import sklearn

ROOT=Path(__file__).resolve().parents[1]
MODEL_NAME='RYMSpotifyClasificadorFavoritos'

def main():
    p=argparse.ArgumentParser(description='Exportar Champion de Registry a archivo local')
    p.add_argument('--tracking-uri',default='http://127.0.0.1:5000',help='Práctica 4: 5000; práctica 5: 5001')
    a=p.parse_args()
    import mlflow
    import mlflow.sklearn
    mlflow.set_tracking_uri(a.tracking_uri)
    uri=f'models:/{MODEL_NAME}@champion'
    print('Cargando:',uri, 'en:',a.tracking_uri)
    modelo=mlflow.sklearn.load_model(uri)
    examples=json.loads((ROOT/'data'/'albumes_ejemplo.json').read_text(encoding='utf-8'))
    from src.config import FEATURE_COLUMNS
    X=pd.DataFrame([{key:examples[0][key] for key in FEATURE_COLUMNS}])
    print('Predicción de control:',int(modelo.predict(X)[0]),float(modelo.predict_proba(X)[0,1]))
    output=ROOT/'models'/'champion.joblib'
    joblib.dump(modelo,output)
    info={'nombre_modelo':MODEL_NAME,'tipo':'Champion exportado de MLflow','modelo_uri':uri,
          'tracking_uri':a.tracking_uri,'sklearn_version':sklearn.__version__,
          'fecha_exportacion_utc':datetime.now(timezone.utc).isoformat(),
          'nota':'Origen: Model Registry de tu máquina. No reinicia automáticamente una API ya encendida.'}
    (ROOT/'models'/'model_info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Exportación terminada:',output)
    print('Reiniciar FastAPI después de exportar.')

if __name__=='__main__':main()
