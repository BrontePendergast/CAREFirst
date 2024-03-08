import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import pymongo

# App to Test
from src.main import app
from src.main import getMessageID
from src.db_mongo import deleteCollection


# Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from typing import Any, Generator
import asyncio

# Mongo
from src.db_mongo import getURI

connection_string= getURI()
client = pymongo.MongoClient(connection_string)
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

# Are we able to send a chat query?
# Do I return the type I expect?
def test_conversations_basic():
    data = {"query": "simple check on my burn"}
    response = client.post(
        "/conversations/30",
        json=data,
    )

    assert response.json()["output"]["conversation_id"] == "30"
    #assert response.json()["conversation_id"] == "30"

    assert response.status_code == 200

    deleteCollection(db_name="carefirstdb", collection_name="messages")


# Are we able to send feedback query?
# Do I return the type I expect?
def test_provide_feedback_basic(): 
    data = {"query": "simple check on my burn"}
    response = client.post(
        "/conversations/30",
        json=data,
    )

    result = database["messages"].find_one({'conversation_id': '30'})
    assert(result['feedback']) == None
    message_id = result["message_id"]

    data = {"feedback": "False"}
    response = client.post(
        "/messages/" + message_id,
        json=data,
    )

    assert response.status_code == 200
    #assert response.json()["feedback"] == False
    assert response.json()["output"]["feedback"] == False

    result = database["messages"].find_one({'message_id': message_id})
    assert(result['feedback']) == False

    deleteCollection(db_name="carefirstdb", collection_name="messages")

# What if we send feedback for a message_id that does not exists in the database?
def test_provide_feedback_no_history(): 
    message_id = '8888'
    data = {"feedback": "False"}
    response = client.post(
        "/messages/" + message_id,
        json=data,
    )

    assert response.status_code == 200
    assert response.json() == None


# If I send multiple queries with the same conversation id, is the message_id different for each one?
def test_multiple_queries():  

    conversation_id = "50"
    queries = ["how to treat a sting?", "how to treat a sting again?", "how to treat a sting again three?"]
    message_id_list = []
    for q in queries:
        data = {"query": q}
        response = client.post(
            "/conversations/" + conversation_id,
            json=data,
        )
        assert response.status_code == 200
        result = database["messages"].find_one({'conversation_id': conversation_id}, sort=[('timestamp_sent_response', pymongo.DESCENDING)])
        message_id_list.append(result['message_id'])

    assert(message_id_list[0] != message_id_list[1])
    assert(message_id_list[1] != message_id_list[2])

    deleteCollection(db_name="carefirstdb", collection_name="messages")