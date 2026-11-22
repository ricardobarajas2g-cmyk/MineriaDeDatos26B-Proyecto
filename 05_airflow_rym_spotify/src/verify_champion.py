"""Cargar Champion desde Model Registry y predecir un álbum del CSV."""
import argparse
from src.config import REGISTRY_MODEL, TRACKING_URI
from src.prepare_data import load_data


def main():
    parser = argparse.ArgumentParser(description="Demostrar inferencia desde Model Registry")
    parser.add_argument("--tracking-uri", default=TRACKING_URI)
    parser.add_argument("--index", type=int, default=0, help="Fila del dataset etiquetado")
    args = parser.parse_args()
    import mlflow
    import mlflow.sklearn
    mlflow.set_tracking_uri(args.tracking_uri)
    model = mlflow.sklearn.load_model(f"models:/{REGISTRY_MODEL}@champion")
    X, y, meta = load_data()
    if args.index < 0 or args.index >= len(X):
        parser.error(f"--index debe estar entre 0 y {len(X)-1}")
    row = X.iloc[[args.index]]
    print("Artista:", meta.iloc[args.index]["artista_rym"])
    print("Álbum:", meta.iloc[args.index]["album_rym"])
    print("RYM real:", meta.iloc[args.index]["rating_rym"])
    print("Probabilidad estimada de favorito:", round(float(model.predict_proba(row)[0, 1]), 4))
    print("Predicción:", int(model.predict(row)[0]))
    print("Demostración con una fila del conjunto general; no representa una predicción nueva sin historial.")


if __name__ == "__main__":
    main()
