"""API interna utilizada por Airflow. No está publicada en el anfitrión.
La API expone los scripts comprobados de la Práctica 4 a través de tareas HTTP.
"""
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from src.config import (DATA_PATH, EXPERIMENT, OUT_DIR, REGISTRY_MODEL,
                        TRACKING_URI)
from src.prepare_data import load_data, dataset_hash, main as prepare_main
from src.train import run_experiment
from src.report import make_report

app = FastAPI(title="Worker didáctico RYM + Spotify", docs_url=None, redoc_url=None)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tasks/validate")
def validate(force_fail: bool = False):
    if force_fail:
        raise HTTPException(status_code=422, detail="Fallo intencional: validación simulada para la práctica")
    X, y, meta = load_data()
    return {"valido": True, "albumes_etiquetados": len(y), "favoritos": int(y.sum()),
            "columnas_predictoras": list(X.columns), "csv_sha256": dataset_hash()[:16]}

@app.post("/tasks/prepare")
def prepare():
    prepare_main()
    return {"resultado": "ok", "archivo": str(OUT_DIR / "albumes_etiquetados.csv"),
            "resumen": str(OUT_DIR / "resumen_datos.json")}

@app.post("/tasks/train")
def train():
    result = run_experiment(tracking_uri=TRACKING_URI, use_mlflow=True, folds=5)
    champion = result["ganador"]
    return {"experimento": EXPERIMENT, "n_modelos": len(result["modelos"]),
            "ganador_cv_f1": champion["modelo"], "cv_f1": champion["cv_f1_mean"],
            "run_id": champion["run_id"]}

@app.post("/tasks/register")
def register():
    summary_file = OUT_DIR / "resumen_experimento.json"
    if not summary_file.is_file():
        raise HTTPException(status_code=409, detail="Primero debe completarse la tarea entrenar_modelos")
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    winner = summary["ganador"]
    model_uri = winner.get("model_uri")
    if not model_uri:
        raise HTTPException(status_code=409, detail="No hay modelo registrado en MLflow")
    from mlflow import MlflowClient, register_model, set_tracking_uri
    set_tracking_uri(TRACKING_URI)
    version = register_model(model_uri=model_uri, name=REGISTRY_MODEL)
    client = MlflowClient(tracking_uri=TRACKING_URI)
    client.set_registered_model_alias(name=REGISTRY_MODEL,
                                      alias="champion", version=version.version)
    return {"modelo": REGISTRY_MODEL, "version": version.version,
            "alias": "champion", "algoritmo": winner["modelo"]}

@app.post("/tasks/report")
def report():
    file = make_report()
    return {"resultado": "ok", "archivo": str(file)}

@app.post("/tasks/verify")
def verify():
    import mlflow.sklearn
    from mlflow import set_tracking_uri
    set_tracking_uri(TRACKING_URI)
    model = mlflow.sklearn.load_model(f"models:/{REGISTRY_MODEL}@champion")
    X, _, meta = load_data()
    row = X.iloc[[0]]
    return {"artista": str(meta.iloc[0]["artista_rym"]),
            "album": str(meta.iloc[0]["album_rym"]),
            "prediccion": int(model.predict(row)[0]),
            "probabilidad": float(model.predict_proba(row)[0, 1])}
