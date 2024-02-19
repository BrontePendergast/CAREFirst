import pytest
from fastapi.testclient import TestClient
from datetime import datetime

# App to Test
from src.main import app

# Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from typing import Any, Generator
import asyncio

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

# Are we able to make a basic prediction?
# Do I return the type I expect?
def test_conversations_basic():
    data = {"conversation_id": '99999', "message_id": "1", "question": "cut"}
    response = client.post(
        "/conversations",
        json=data,
    )

    # conversation_id, message_id, page_content, source, timestamp
    assert response.status_code == 200
    assert response.json()["output"][0] == '99999'
    assert response.json()["output"][1] == "1"
    assert response.json()["output"][2] == "Cuts and Scrapes\nA cut is a wound where the skin has been split open. The edges of the \ncut can be jagged or smooth. Scrapes are wounds where the skin has \nbeen rubbed or scraped away. Signs and symptoms of a cut or scrape may \ninclude pain and bleeding.\nWhat to Do\nCall\nCall EMS/9-1-1 if you suspect that there may be more serious injuries.\nCare\n1.There is usually minimal bleeding with cuts and scrapes, but if\nthe wound is bleeding significantly, apply direct pressure until it\nstops.\n2.If possible, rinse the wound for 5\nminutes with clean, running tap\nwater.3.If an antibiotic ointment or\ncream is available, ask the\nperson if he or she has a\nsensitivity to any antibiotics,\nsuch as penicillin. If not, suggest\nthe person apply it to the\nwound.\n4.Cover the wound with a\nsterile non-stick dressing\nand/or bandage.\n5.Ensure that the person\nknows to watch for signs\nof infection over the next\nfew days.\n8787\nWound Care87"
    assert response.json()["output"][3] == 'page 91 of redcross_guidelines.pdf'

    assert type(response.json()["output"][0]) is str
    

    # Are we able to make a basic prediction?
# Do I return the type I expect?
def test_messages_basic():
    data = {"conversation_id": '99999', "message_id": "1", "user_feedback": True}
    response = client.post(
        "/messages",
        json=data,
    )
    # conversation_id, message_id, page_content, source, timestamp
    assert response.status_code == 200
    