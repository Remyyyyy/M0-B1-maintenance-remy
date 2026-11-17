"""Tests fonctionnels de l'endpoint /predict."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

VALID_PAYLOAD = {
    "type_machine": "compresseur",
    "age_machine_jours": 1500,
    "derniere_maintenance_jours": 45,
    "temperature_moyenne": 68.5,
    "vibration_moyenne": 3.2,
    "pression_moyenne": 7.8,
    "nb_incidents_3_mois": 2,
}

payload = VALID_PAYLOAD.copy()

def test_predict_valid_returns_200() -> None:
    with TestClient(app) as client:
        r = client.post("/predict", json=VALID_PAYLOAD)
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {"criticite", "probabilites"}
        assert body["criticite"] in {"basse", "moyenne", "haute"}
        assert set(body["probabilites"].keys()) == {"basse", "moyenne", "haute"}

def test_predict_invalid_type_machine_returns_422() -> None:
    payload = VALID_PAYLOAD.copy()
    payload["type_machine"] = "scooter"
    with TestClient(app) as client:
        r = client.post("/predict", json=payload)
        assert r.status_code == 422

@pytest.mark.parametrize(
    "type_machine",
    ["pompe", "compresseur", "convoyeur", "presse", "four"],
)
def test_predict_all_machine_types(type_machine: str) -> None:
    """Chaque type de machine valide doit renvoyer 200."""
    payload = VALID_PAYLOAD.copy()
    payload["type_machine"] = type_machine
    with TestClient(app) as client:
        r = client.post("/predict", json=payload)
        assert r.status_code == 200


