

def test_api_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_ollama_health_endpoint(client):
    res = client.get("/api/health/ollama")
    assert res.status_code == 200
    data = res.json()
    assert "available" in data
