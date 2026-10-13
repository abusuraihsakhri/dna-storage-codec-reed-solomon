"""Backend smoke tests: APIs plus serving the static browser codec."""
import os
os.environ.setdefault("AUDIT_SECRET_KEY", "test-only-security-key-not-for-production")
from fastapi.testclient import TestClient
from agents.api import app
from dna_storage_codec.server import create_app

def test_legacy_api_and_frontend():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        landing = client.get("/")
        assert landing.status_code == 200
        assert "DNA Storage Codec" in landing.text
        module = client.get("/codec.mjs")
        assert module.status_code == 200
        assert "encodeBytes" in module.text
        payload = {
            "task_id": "A",
            "target_identifier": "B",
            "primary_metric": 0.0,
            "secondary_metric": 0.0,
            "status_descriptor": "NOMINAL",
            "is_critical_flag": False,
        }
        response = client.post("/api/audit", json=payload)
        assert response.status_code == 200
        assert response.json()["total_alerts"] == 0
        assert client.post("/api/audit", json={**payload, "primary_metric": float("nan")}).status_code == 422
        assert client.get("/api/audit/logs").json()["verified"] is True

def test_package_api_and_frontend():
    package_app = create_app()
    assert package_app is not None
    with TestClient(package_app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/codec.mjs").status_code == 200
