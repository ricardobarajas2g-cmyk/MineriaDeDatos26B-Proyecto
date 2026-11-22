import numpy as np
from src.config import FEATURE_COLUMNS
from src.prepare_data import load_data


def test_datos_favoritos():
    X, y, meta = load_data()
    assert len(y) == 611
    assert set(y.unique()) == {0, 1}
    assert y.sum() == 291
    assert list(X.columns) == FEATURE_COLUMNS
    assert meta["rating_rym"].notna().all()


def test_sin_fuga_target():
    X, _, _ = load_data()
    for forbidden in ("rating_rym", "favorito_9_10", "canciones_me_gusta", "proporcion_me_gusta"):
        assert forbidden not in X.columns
    assert X["generos_frecuentes"].notna().all()
