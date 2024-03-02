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
    assert response.status_code == 200

    deleteCollection(db_name="carefirstdb", collection_name="messages")

# If I send multiple queries with the same conversation id, is the message_id correctly updated in the database
def test_multiple_queries():  
    conversation_id = "50"
    queries = ["how to treat a sting?", "how to treat a sting again?", "how to treat a sting again three?"]
    message_nums = [0, 1, 2]
    for q, num in zip(queries, message_nums):
        data = {"query": q}
        response = client.post(
            "/conversations/" + conversation_id,
            json=data,
        )
        assert response.status_code == 200
        result = database["messages"].find_one({'conversation_id': conversation_id}, sort=[('timestamp', pymongo.DESCENDING)])
        assert(result['message_id']) == num
   
    deleteCollection(db_name="carefirstdb", collection_name="messages")

# If I send user feedback, is does the database update properly?
def test_provide_feedback(): 
    conversation_id = "50"
    queries = ["how to treat a sting?", "how to treat a sting again?", "how to treat a sting again three?"]
    message_nums = [0, 1, 2]
    for q, num in zip(queries, message_nums):
        data = {"query": q}
        response = client.post(
            "/conversations/" + conversation_id,
            json=data,
        )

    data = {"feedback": "False"}
    response = client.post(
        "/messages/" + conversation_id,
        json=data,
    )
    
    result = database["messages"].find_one({'conversation_id': conversation_id, 'message_id': 2})
    assert(result['feedback']) == False

    deleteCollection(db_name="carefirstdb", collection_name="messages")

