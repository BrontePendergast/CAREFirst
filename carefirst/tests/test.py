import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import pymongo

# App to Test
from src.main import app
from src.db_mongo import deleteCollection


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
def test_conversations_basic():
    data = {"question": "simple check on my burn"}
    response = client.post(
        "/conversations/30",
        json=data,
    )
    
    assert response.status_code == 200

    deleteCollection(db_name="carefirstdb", collection_name="messages")

def test_conversations_chatlog():
    data1 = {"question": "broke my toe first"}
    response1 = client.post(
        "/conversations/40",
        json=data1,
    )
    
    message_id_1 =  database["messages"].find_one({'conversation_id' : "40", 'message_id' : 0})['message_id']
    
    data2 = {"question": "broke my arm second"}
    response2 = client.post(
        "/conversations/40",
        json=data2,
    )  
    
    message_id_2 =  database["messages"].find_one({'conversation_id' : "40", 'message_id' : 1})["message_id"]


    assert response1.status_code == 200
    assert response2.status_code == 200

    assert response1.json()["output"][0] == '40'
    assert response2.json()["output"][0] == '40'

    assert message_id_1 != message_id_2
    
    deleteCollection(db_name="carefirstdb", collection_name="messages")

def test_feedback_basic():
    data = {"message_id": 0, "user_feedback": True}
    response = client.post(
        "/messages/50",
        json=data,
    )
    
    assert response.status_code == 200
    assert response.json()["output"]["id"] == "50"
    assert response.json()["output"]["message_id"] == 0
    assert response.json()["output"]["user_feedback"] == True

    deleteCollection(db_name="carefirstdb", collection_name="messages")

