import pytest
from fastapi.testclient import TestClient


from src.main import app

client = TestClient(app)

def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200

# Are we able to make a basic prediction?
# Do I return the type I expect?
def test_predict_basic2():
    data = {"query": "cut"}
    response = client.post(
        "/predict",
        json=data,
    )
    print(response)
    assert response.status_code == 200
    # assert type(response.json()["prediction"]) is str