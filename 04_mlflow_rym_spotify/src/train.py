"""Comparación justa de 3 modelos: CV train para seleccionar, holdout para informar."""
import argparse
import json
from pathlib import Path
import tempfile

import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split, cross_validate
from src.config import (DATA_PATH, EXPERIMENT, FEATURE_COLUMNS, OUT_DIR, SEED, TARGET, TRACKING_URI)
from src.prepare_data import dataset_hash, load_data
from src.models import make_pipeline, model_params
from src.evaluate import compute_metrics, save_artifacts


def run_experiment(tracking_uri=TRACKING_URI, use_mlflow=True, folds=5, test_size=0.2):
    """Entrena y registra modelos; datos de test no intervienen en selección Champion."""
    X, y, metadata = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=SEED, stratify=y
    )
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=SEED)
    out = []
    if use_mlflow:
        import mlflow
        import mlflow.sklearn
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(EXPERIMENT)
    for name in ("logistic", "forest", "svm"):
        model = make_pipeline(name)
        cross = cross_validate(
            model, X_train, y_train, cv=cv,
            scoring={"f1": "f1", "accuracy": "accuracy", "roc_auc": "roc_auc"},
            n_jobs=1,
        )
        model.fit(X_train, y_train)
        metrics = compute_metrics(model, X_test, y_test)
        values = {
            "modelo": name,
            "cv_f1_mean": float(cross["test_f1"].mean()),
            "cv_f1_std": float(cross["test_f1"].std()),
            "cv_accuracy_mean": float(cross["test_accuracy"].mean()),
            "cv_roc_auc_mean": float(cross["test_roc_auc"].mean()),
            **{f"test_{key}": val for key, val in metrics.items()},
        }
        with tempfile.TemporaryDirectory() as tmp:
            save_artifacts(model, X_test, y_test, tmp)
            if use_mlflow:
                with mlflow.start_run(run_name=name) as run:
                    mlflow.log_params({"algoritmo": name, "test_size": test_size,
                                       "n_splits": folds, "seed": SEED,
                                       "hash_csv": dataset_hash()[:16],
                                       **model_params(name)})
                    mlflow.log_metrics({k:v for k,v in values.items() if k != "modelo"})
                    mlflow.set_tags({"proyecto": "RYM + Spotify", "target": TARGET,
                                     "split": "stratified_holdout", "seleccion": "cv_f1_mean"})
                    mlflow.log_artifacts(tmp, artifact_path="evaluacion")
                    info = mlflow.sklearn.log_model(
                        sk_model=model,
                        name="modelo",
                        input_example=X_train.head(2).copy(),
                        serialization_format="cloudpickle"
                    )
                    values["run_id"] = run.info.run_id
                    values["model_uri"] = info.model_uri
            else:
                values["run_id"] = None
                values["model_uri"] = None
        out.append(values)
        print(f"{name:9s} | CV F1={values['cv_f1_mean']:.3f} | test F1={values['test_f1']:.3f} | test ROC-AUC={values['test_roc_auc']:.3f}")
    # Seleccionar según CV exclusivamente: test independiente reservado para evaluación.
    winner = max(out, key=lambda d: d["cv_f1_mean"])
    OUT_DIR.mkdir(exist_ok=True)
    pd.DataFrame(out).to_csv(OUT_DIR / "comparacion_modelos.csv", index=False, encoding="utf-8-sig")
    summary = {
        "experimento": EXPERIMENT, "datos_originales": str(DATA_PATH.name),
        "sha256_csv": dataset_hash(), "n_albums": int(len(y)),
        "n_train": int(len(y_train)), "n_test": int(len(y_test)),
        "variables_predictoras": FEATURE_COLUMNS, "target": TARGET,
        "criterio_seleccion": "mayor cv_f1_mean (solo entrenamiento)",
        "ganador": winner, "modelos": out,
        "advertencia": "No elegir nuevos hiperparametros basandose en el conjunto test",
    }
    (OUT_DIR / "resumen_experimento.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGanador por CV F1: {winner['modelo']} (CV F1={winner['cv_f1_mean']:.3f})")
    print("Resultados:", OUT_DIR)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Comparar Logistic, RF y SVM con MLflow")
    parser.add_argument("--tracking-uri", default=TRACKING_URI)
    parser.add_argument("--sin-mlflow", action="store_true", help="Validación local rápida; no registra runs")
    parser.add_argument("--folds", type=int, default=5)
    args = parser.parse_args()
    if args.folds < 2:
        parser.error("--folds debe ser al menos 2")
    run_experiment(tracking_uri=args.tracking_uri, use_mlflow=not args.sin_mlflow, folds=args.folds)


if __name__ == "__main__":
    main()
