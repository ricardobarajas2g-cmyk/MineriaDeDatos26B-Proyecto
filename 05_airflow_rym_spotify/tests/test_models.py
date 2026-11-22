from src.prepare_data import load_data
from src.models import make_pipeline
from sklearn.metrics import f1_score


def test_modelos_entrenan_y_predicen():
    X, y, _ = load_data()
    X, y = X.iloc[:180], y.iloc[:180]
    for name in ("logistic", "forest", "svm"):
        model = make_pipeline(name)
        model.fit(X, y)
        pred = model.predict(X.iloc[:5])
        prob = model.predict_proba(X.iloc[:5])
        assert len(pred) == 5
        assert prob.shape == (5, 2)
        assert ((prob >= 0) & (prob <= 1)).all()
