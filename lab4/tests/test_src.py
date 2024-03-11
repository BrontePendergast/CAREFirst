from fastapi.testclient import TestClient

from src.main import app

# putest fixture
import pytest

# Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from typing import Any, Generator
import asyncio

client = TestClient(app)


@pytest.fixture(autouse=True)
def _init_cache() -> Generator[Any, Any, None]:
    FastAPICache.init(InMemoryBackend())
    yield
    asyncio.run(FastAPICache.clear())


# @pytest.fixture
# def client():
#     FastAPICache.init(InMemoryBackend())
#     with TestClient(app) as c:
#         yield c


# Rquirement #1
def test_read_hello_name():
    response = client.get("/hello", params={"name": "Ricardo"})
    assert response.json()["message"] == "hello Ricardo"
    assert response.status_code == 200


# Rquirement #2
def test_read_hello_error():
    response = client.get("/hello")
    assert response.status_code == 422


# Rquirement #3
def test_read_root():
    response = client.get("/")
    assert response.status_code == 404


# Rquirement #4
def test_read_docs():
    response = client.get("/docs")
    assert response.status_code == 200


# Rquirement #5
def test_read_openapi():
    response = client.get("/openapi.json")
    assert int(response.json()["openapi"][0]) >= 3
    assert response.status_code == 200


# Addiotional Tests #1 very long name
def test_hello_endpoint_long_name():
    long_name = "A" * 9999
    response = client.get(f"/hello?name={long_name}")
    assert response.json()["message"] == f"hello {long_name}"
    assert response.status_code == 200


# Addiotional Tests #2 empty name
def test_hello_empty_name():
    response = client.get(f"/hello?name=")
    assert response.json()["message"] == f"hello "
    assert response.status_code == 200


# Addiotional Tests #3 name with special character
def test_hello_special_characters():
    response = client.get("/hello?name=José")
    assert response.json()["message"] == f"hello José"
    assert response.status_code == 200


# Addiotional Tests #4 Test with multiple names
def test_hello_with_multiple_names():
    response = client.get("/hello?name=Ricardo Andres")
    assert response.status_code == 200
    assert response.json() == {"message": "hello Ricardo Andres"}


# Addiotional Tests #5 Test docs endpoint with wrong parameters
def test_docs_wrong_parameters():
    response = client.get("/docs?name=Ricardo Andres")
    assert response.status_code == 200


# Lab2
# Test 1 prediction
def test_prediction():
    payload = {
        "MedInc": 8.3252,
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 37.88,
        "Longitude": -122.23,
    }
    response = client.post("/predict", json=payload)
    house_value = float(response.json()["house_value"])
    assert house_value == 4.413388694639975
    assert response.status_code == 200


# Test 2 MedInc no negative
def test_medinc_no_negative():
    payload = {
        "MedInc": -8.3252,
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 37.88,
        "Longitude": -122.23,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


# Test 3 Healthcheck test
def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200


# Test 4 Missing value test
def test_missing_value():
    payload = {
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 37.88,
        "Longitude": -122.23,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


# Test 4 Value in wrong Format
def test_wrong_value_format():
    payload = {
        "MedInc": "Holi",
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 37.88,
        "Longitude": -122.23,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


# Test 5 Extreme longitude
def test_wrong_longitude():
    payload = {
        "MedInc": "Holi",
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 37.88,
        "Longitude": 115,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


# Test 6 Extreme latitude
def test_wrong_latitude():
    payload = {
        "MedInc": "Holi",
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 31,
        "Longitude": -122.23,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


# Test 7 Out of order fields
def test_out_of_order():
    payload_1 = {
        "MedInc": 8.3252,
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 37.88,
        "Longitude": -122.23,
    }
    response_1 = client.post("/predict", json=payload_1)
    assert response_1.status_code == 200
    house_value_1 = float(response_1.json()["house_value"])
    payload_2 = {
        "Longitude": -122.23,
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 37.88,
        "MedInc": 8.3252,
    }
    response_2 = client.post("/predict", json=payload_2)
    assert response_2.status_code == 200
    house_value_2 = float(response_2.json()["house_value"])
    assert house_value_1 == house_value_2


# Test 8 Extra field
def test_extra_field():
    payload = {
        "MedInc": 8.3252,
        "HouseAge": 41,
        "AveRooms": 6.98412698,
        "AveBedrms": 1.02380952,
        "Population": 322,
        "AveOccup": 2.55555556,
        "Latitude": 37.88,
        "Longitude": -122.23,
        "new_field": 123456,
    }
    response = client.post("/predict", json=payload)
    house_value = float(response.json()["house_value"])
    assert house_value == 4.413388694639975
    assert response.status_code == 200


# Lab3
# Test 1 Bulk prediction
def test_bulk_prediction():
    payload = {
        "houses": [
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
        ]
    }
    response = client.post("/bulk_predict", json=payload)

    house_values = response.json()["house_values"]
    house_value_1 = house_values[0]
    house_value_2 = house_values[1]

    assert house_value_1 == 4.413388694639975
    assert house_value_2 == 4.413388694639975
    assert len(payload["houses"]) == len(house_values)
    assert response.status_code == 200


# Test 2 Bulk MedInc no negative
def test_bulk_medinc_no_negative():
    payload = {
        "houses": [
            {
                "MedInc": -8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
            {
                "MedInc": 8.3252,
                "HouseAge": -41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
        ]
    }
    response = client.post("/bulk_predict", json=payload)
    assert response.status_code == 422


# Test 4 Missing value test
def test_bulk_missing_value():
    payload = {
        "houses": [
            {
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
            {
                "MedInc": 8.3252,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
        ]
    }
    response = client.post("/bulk_predict", json=payload)
    assert response.status_code == 422


# Test 4 Value in wrong Format
def test_bulk_wrong_value_format():
    payload = {
        "houses": [
            {
                "MedInc": "Holi",
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
            {
                "MedInc": 8.3252,
                "HouseAge": "Holi",
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
        ]
    }
    response = client.post("/bulk_predict", json=payload)
    assert response.status_code == 422


# Test 5 Extreme longitude
def test_bulk_wrong_longitude():
    payload = {
        "houses": [
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": 115,
            },
        ]
    }
    response = client.post("/bulk_predict", json=payload)
    assert response.status_code == 422


# Test 6 Extreme latitude
def test_bulk_wrong_latitude():
    payload = {
        "houses": [
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 31,
                "Longitude": -122.23,
            },
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
        ]
    }
    response = client.post("/bulk_predict", json=payload)
    assert response.status_code == 422


# Test 7 Out of order fields
def test_bulk_out_of_order():
    payload_1 = {
        "houses": [
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
        ]
    }
    response_1 = client.post("/bulk_predict", json=payload_1)
    assert response_1.status_code == 200
    house_value_1 = float(response_1.json()["house_values"][0])
    payload_2 = {
        "houses": [
            {
                "Longitude": -122.23,
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
            },
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "AveOccup": 2.55555556,
                "Population": 322,
                "Latitude": 37.88,
                "Longitude": -122.23,
            },
        ]
    }
    response_2 = client.post("/bulk_predict", json=payload_2)
    assert response_2.status_code == 200
    house_value_2 = float(response_2.json()["house_values"][0])
    assert house_value_1 == house_value_2


# Test 8 Extra field
def test_bulk_extra_field():
    payload = {
        "houses": [
            {
                "Longitude": -122.23,
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "Population": 322,
                "AveOccup": 2.55555556,
                "Latitude": 37.88,
            },
            {
                "MedInc": 8.3252,
                "HouseAge": 41,
                "AveRooms": 6.98412698,
                "AveBedrms": 1.02380952,
                "AveOccup": 2.55555556,
                "Population": 322,
                "Latitude": 37.88,
                "Longitude": -122.23,
                "new_field": 12345,
            },
        ]
    }
    response = client.post("/bulk_predict", json=payload)
    house_value = float(response.json()["house_values"][0])
    assert house_value == 4.413388694639975
    assert response.status_code == 200
