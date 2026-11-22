from fastapi.testclient import TestClient
from worker.service import app


def test_worker_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_validar_csv():
    client = TestClient(app)
    response = client.post("/tasks/validate")
    assert response.status_code == 200
    assert response.json()["albumes_etiquetados"] == 611
    assert response.json()["favoritos"] == 291


def test_fallo_intencional():
    client = TestClient(app)
    response = client.post("/tasks/validate?force_fail=true")
    assert response.status_code == 422
    assert "Fallo intencional" in response.json()["detail"]
