
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import rate_limiter


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_buckets():
    rate_limiter.buckets.clear()
    yield
    rate_limiter.buckets.clear()


def test_configure_bucket():
    response = client.post(
        "/api/limit/configure",
        json={
            "client_id": "user1",
            "capacity": 3,
            "refill_rate": 1,
            "refill_interval_seconds": 10,
        },
    )

    assert response.status_code == 201
    assert response.json()["capacity"] == 3
    assert response.json()["available_tokens"] == 3


def test_requests_are_allowed_until_tokens_run_out():
    client.post(
        "/api/limit/configure",
        json={
            "client_id": "user1",
            "capacity": 2,
            "refill_rate": 1,
            "refill_interval_seconds": 60,
        },
    )

    first = client.post("/api/limit/user1")
    second = client.post("/api/limit/user1")
    third = client.post("/api/limit/user1")

    assert first.status_code == 200
    assert first.json()["allowed"] is True

    assert second.status_code == 200
    assert second.json()["remaining_tokens"] == 0

    assert third.status_code == 429
    assert third.json()["allowed"] is False
    assert "Retry-After" in third.headers


def test_unknown_client_returns_404():
    response = client.post("/api/limit/unknown")

    assert response.status_code == 404


def test_bucket_status():
    client.post(
        "/api/limit/configure",
        json={
            "client_id": "user1",
            "capacity": 3,
            "refill_rate": 1,
            "refill_interval_seconds": 10,
        },
    )

    response = client.get("/api/limit/user1")

    assert response.status_code == 200
    assert response.json()["client_id"] == "user1"
    assert response.json()["capacity"] == 3


def test_token_refills_after_time_passes(monkeypatch):
    clock = [100.0]

    monkeypatch.setattr(
        rate_limiter.time,
        "monotonic",
        lambda: clock[0],
    )

    rate_limiter.configure_bucket(
        client_id="user1",
        capacity=1,
        refill_rate=1,
        refill_interval_seconds=10,
    )

    assert rate_limiter.consume_token("user1")["allowed"] is True
    assert rate_limiter.consume_token("user1")["allowed"] is False

    clock[0] += 10

    result = rate_limiter.consume_token("user1")
    assert result["allowed"] is True
