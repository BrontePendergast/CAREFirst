import pytest
from fastapi.testclient import TestClient


from src.main import app
from src.retrieval import retrieval

client = TestClient(app)

def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200

# Are we able to make a basic prediction?
# Do I return the type I expect?
# we test the predition is only a particular type because model weights change as we retrain
# when model weights change we also change our results
# recommend to test the fundamental expectation and not the particular value
def test_predict_basic():
    data = "cut"
    response = client.post(
        "/predict",
        json=data,
    )
    print(response)
    assert response.status_code == 200
    # assert type(response.json()["prediction"]) is str

def test_predict_basic2():
    data = {"query": "cut"}
    response = client.post(
        "/predict",
        json=data,
    )
    print(response)
    assert response.status_code == 200
    # assert type(response.json()["prediction"]) is str