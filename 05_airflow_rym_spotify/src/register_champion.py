"""Registrar modelo elegido por CV con alias champion usando resumen del entrenamiento."""
import argparse
import json
from src.config import OUT_DIR, REGISTRY_MODEL, TRACKING_URI


def main():
    parser = argparse.ArgumentParser(description="Registrar el mejor modelo en MLflow")
    parser.add_argument("--tracking-uri", default=TRACKING_URI)
    args = parser.parse_args()
    result_path = OUT_DIR / "resumen_experimento.json"
    if not result_path.exists():
        raise SystemExit("Ejecutar primero python -m src.train (CON MLflow) para crear el resumen")
    summary = json.loads(result_path.read_text(encoding="utf-8"))
    champion = summary["ganador"]
    if not champion.get("model_uri"):
        raise SystemExit("Los runs se generaron con --sin-mlflow; repetir sin ese argumento")
    import mlflow
    from mlflow.tracking import MlflowClient
    mlflow.set_tracking_uri(args.tracking_uri)
    version = mlflow.register_model(model_uri=champion["model_uri"], name=REGISTRY_MODEL)
    client = MlflowClient(tracking_uri=args.tracking_uri)
    client.set_registered_model_alias(name=REGISTRY_MODEL, alias="champion", version=version.version)
    print(f"Modelo: {REGISTRY_MODEL}; versión: {version.version}; alias: champion")
    print(f"Origen: {champion['modelo']} (F1 CV: {champion['cv_f1_mean']:.3f})")


if __name__ == "__main__":
    main()
