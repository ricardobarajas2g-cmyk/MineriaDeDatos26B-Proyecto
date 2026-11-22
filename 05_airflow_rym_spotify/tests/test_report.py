import json
from src.report import make_report


def test_report_tiene_ganador(tmp_path):
    summary = {"modelos": [{"modelo": "logistic", "cv_f1_mean": 0.53, "test_f1": 0.58,
                             "test_roc_auc": 0.60}], "ganador": {"modelo": "logistic"}}
    data = {"filas_etiquetadas": 611, "favoritos": 291, "no_favoritos": 320,
            "sha256_csv": "abc123"}
    (tmp_path / "resumen_experimento.json").write_text(json.dumps(summary), encoding="utf-8")
    (tmp_path / "resumen_datos.json").write_text(json.dumps(data), encoding="utf-8")
    path = make_report(tmp_path)
    assert path.exists()
    assert "Regresión" not in path.read_text(encoding="utf-8")
    assert "logistic" in path.read_text(encoding="utf-8")
    assert "611" in path.read_text(encoding="utf-8")
