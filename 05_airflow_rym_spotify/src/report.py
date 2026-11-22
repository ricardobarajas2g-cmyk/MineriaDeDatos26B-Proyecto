"""Reporte consolidado de la ejecución. Se genera al final del DAG."""
import json
from pathlib import Path
from src.config import OUT_DIR, REGISTRY_MODEL


def make_report(directory=OUT_DIR):
    directory = Path(directory)
    summary_path = directory / "resumen_experimento.json"
    data_path = directory / "resumen_datos.json"
    if not summary_path.exists() or not data_path.exists():
        raise FileNotFoundError("Faltan resultados; ejecutar validar/preparar/entrenar primero")
    s = json.loads(summary_path.read_text(encoding="utf-8"))
    d = json.loads(data_path.read_text(encoding="utf-8"))
    lines = ["# Informe automatizado de RYM + Spotify", "",
             f"Álbumes con etiqueta: {d['filas_etiquetadas']}",
             f"Favoritos: {d['favoritos']}",
             f"No favoritos: {d['no_favoritos']}",
             f"SHA-256 del CSV: `{d['sha256_csv']}`", "",
             "## Comparación de modelos", "",
             "| Modelo | CV F1 | F1 test | ROC-AUC test |", "|---|---:|---:|---:|"]
    for model in s["modelos"]:
        lines.append(f"| {model['modelo']} | {model['cv_f1_mean']:.3f} | "
                     f"{model['test_f1']:.3f} | {model['test_roc_auc']:.3f} |")
    winner = s["ganador"]
    lines.extend(["", f"**Ganador según validación cruzada:** {winner['modelo']}",
                  f"**Modelo Registry:** `{REGISTRY_MODEL}@champion`", "",
                  "Nota: el conjunto de prueba no se utiliza para seleccionar el Champion."])
    output = directory / "informe_airflow.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output

if __name__ == "__main__":
    print(make_report())
