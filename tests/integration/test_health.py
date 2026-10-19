from fastapi.testclient import TestClient


def test_health_without_session_returns_only_status(client: TestClient) -> None:
    """AC-4: no session needed; the body holds the status and nothing else."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_answers_head_for_monitoring_tools(client: TestClient) -> None:
    """AC-4: HEAD-based monitors see the check as up."""
    response = client.head("/api/health")

    assert response.status_code == 200
