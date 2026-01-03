import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_extract_itinerary_demo_mode():
    os.environ["DEMO_MODE"] = "true"

    payload = {
        "text": "We are 2 people. 4 days in Sri Lanka. Land in Colombo, want Kandy and Ella, train ride.",
        "max_days": 10,
        "currency": "LKR",
    }
    r = client.post("/extract-itinerary", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["currency"] == "LKR"
    assert data["duration_days"] >= 1
    assert len(data["days"]) == data["duration_days"]
