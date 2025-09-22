import pytest
import requests

# L'URL di base punta alla porta 80 del proxy Nginx
BASE_URL = "http://127.0.0.1:80"


def test_health_check_endpoint():
    """Tests the /health endpoint for a 200 OK response."""
    # AGGIUNTO IL PREFISSO /schedule/
    response = requests.get(f"{BASE_URL}/schedule/health")
    assert response.status_code == 200
    response_json = response.json()
    assert "status" in response_json
    assert response_json["status"] == "ok"


def test_get_lessons_endpoint_invalid_request():
    """Tests the /lessons endpoint for a 400 Bad Request error on invalid payload."""
    # AGGIUNTO IL PREFISSO /schedule/
    response = requests.post(f"{BASE_URL}/schedule/lessons", json={})
    assert response.status_code == 400