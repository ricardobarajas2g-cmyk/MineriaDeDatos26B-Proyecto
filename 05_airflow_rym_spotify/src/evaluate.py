"""Métricas y figuras para MLflow."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, ConfusionMatrixDisplay, RocCurveDisplay,
                             classification_report)


def compute_metrics(model, X, y):
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]
    return {
        "accuracy": float(accuracy_score(y, y_pred)),
        "precision": float(precision_score(y, y_pred, zero_division=0)),
        "recall": float(recall_score(y, y_pred, zero_division=0)),
        "f1": float(f1_score(y, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, y_prob)),
    }


def save_artifacts(model, X_test, y_test, dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    cm = ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, display_labels=["No favorito", "Favorito"], cmap="Blues")
    cm.ax_.set_title("Matriz de confusión · test")
    cm.figure_.tight_layout()
    cm.figure_.savefig(dest / "matriz_confusion.png", dpi=140)
    plt.close(cm.figure_)
    roc = RocCurveDisplay.from_estimator(model, X_test, y_test)
    roc.ax_.set_title("Curva ROC · test")
    roc.figure_.tight_layout()
    roc.figure_.savefig(dest / "curva_roc.png", dpi=140)
    plt.close(roc.figure_)
    (dest / "reporte_clasificacion.txt").write_text(
        classification_report(y_test, model.predict(X_test), target_names=["No favorito", "Favorito"], zero_division=0),
        encoding="utf-8"
    )
