import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import pymongo

# App to Test
from src.main import app

# Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from typing import Any, Generator
import asyncio

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["carefirstdb"]

@pytest.fixture(autouse=True)
def _init_cache() -> Generator[Any, Any, None]:
    FastAPICache.init(InMemoryBackend())
    yield
    asyncio.run(FastAPICache.clear())

# Init
client = TestClient(app)

def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200

@pytest.mark.parametrize(
    "test_input, expected",
    [("james", "james"), ("bob", "bob"), ("BoB", "BoB"), (100, 100)],
)

def test_hello(test_input, expected):
    response = client.get(f"/hello?name={test_input}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Hello {expected}"}

# # Are we able to make a basic prediction?
# # Do I return the type I expect?
# def test_conversations_basic():
#     data = {"question": "simple check on my burn"}
#     response = client.post(
#         "/conversations/40",
#         json=data,
#     )
    
#     assert response.status_code == 200

def test_conversations_history_update():
    data1 = {"question": "broke my toe first"}
    response1 = client.post(
        "/conversations/999",
        json=data1,
    )
    
    message_id_1 =  database["history"].find_one({'conversation_id' : "999"})['message_id']
    #history_1 =  database["history"].find_one({'conversation_id' : "999"})['history']
    
    data2 = {"question": "broke my arm second"}
    response2 = client.post(
        "/conversations/999",
        json=data2,
    )  
    
    message_id_2 =  database["history"].find_one({'conversation_id' : "999"})["message_id"]
    #history_2 =  database["history"].find_one({'conversation_id' : "999"})['history']


    assert response1.status_code == 200
    assert response2.status_code == 200

    assert response1.json()["output"][0] == '999'
    assert response2.json()["output"][0] == '999'

    assert message_id_1 != message_id_2
    #assert history_1 != history_2  