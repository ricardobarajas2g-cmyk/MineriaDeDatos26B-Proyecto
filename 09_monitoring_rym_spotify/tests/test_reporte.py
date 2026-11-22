import json
import sys
import types

import pytest

from monitoring.generar_reporte import extraer_resumen_evidently, reportar
from monitoring.generar_demo import generar_demo
from monitoring.preparar_datos import preparar
from monitoring.config import DATA_ORIGINAL


def test_parseo_metricas_evidently_acepta_faltantes():
    assert extraer_resumen_evidently({'metrics':[]})['columnas_con_drift'] is None


def test_parseo_metricas_evidently_estructura_documentada():
    ejemplo = {'metrics': [
        {'metric_name': 'DriftedColumnsCount', 'value': {'count': 3, 'share': .3}},
        {'metric_name': 'ValueDrift', 'config': {'column':'promedio_energy'}, 'value': .015}
    ]}
    result = extraer_resumen_evidently(ejemplo)
    assert result['columnas_con_drift'] == 3
    assert result['fraccion_columnas_con_drift'] == .3
    assert result['detalle_por_columna']['promedio_energy']['valor_metrica'] == .015


def test_reporte_interfaz_con_evidently_simulado(tmp_path, monkeypatch):
    # Test de integración de las llamadas; no sustituye prueba real con Evidently instalado.
    calls = {}
    class DummyDataDefinition:
        def __init__(self, **kwargs):
            calls['schema'] = kwargs
    class DummyDataset:
        @classmethod
        def from_pandas(cls, df, data_definition):
            assert len(df.columns) == 10
            return df
    class DummyDriftPreset:
        def __init__(self, columns):
            calls['features'] = columns
    class DummySnapshot:
        def save_html(self, path):
            from pathlib import Path
            Path(path).write_text('<html>simulado</html>', encoding='utf-8')
        def save_json(self, path):
            from pathlib import Path
            Path(path).write_text(json.dumps(self.dict()), encoding='utf-8')
        def dict(self):
            return {'metrics': []}
    class DummyReport:
        def __init__(self, metrics):
            assert len(metrics) == 1
        def run(self, current, reference):
            calls['n_actual'] = len(current)
            calls['n_referencia'] = len(reference)
            return DummySnapshot()
    mod = types.ModuleType('evidently')
    mod.Dataset = DummyDataset
    mod.DataDefinition = DummyDataDefinition
    mod.Report = DummyReport
    pre = types.ModuleType('evidently.presets')
    pre.DataDriftPreset = DummyDriftPreset
    monkeypatch.setitem(sys.modules, 'evidently', mod)
    monkeypatch.setitem(sys.modules, 'evidently.presets', pre)
    ref = tmp_path / 'ref.csv'
    preparar(DATA_ORIGINAL, ref)
    logs = generar_demo(DATA_ORIGINAL, tmp_path / 'demo.jsonl', cantidad=50)
    resumen, html = reportar(ref, logs, tmp_path / 'reports')
    assert resumen['referencia_filas'] == 611
    assert resumen['actual_filas'] == 50
    assert resumen['solicitudes_sinteticas']
    assert (tmp_path / 'reports' / 'resumen_monitoreo.md').exists()
    assert html.exists()
    assert calls['n_referencia'] == 611
    assert calls['n_actual'] == 50
    assert calls['schema']['categorical_columns'] == ['genero_principal']


def test_reporte_no_acepta_muestra_demasiado_pequena(tmp_path):
    ref = tmp_path / 'ref.csv'
    preparar(DATA_ORIGINAL, ref)
    logs = generar_demo(DATA_ORIGINAL, tmp_path / 'demo.jsonl', cantidad=10)
    with pytest.raises(ValueError, match='mínimo 20'):
        reportar(ref, logs, tmp_path / 'reports', minimo=20)
