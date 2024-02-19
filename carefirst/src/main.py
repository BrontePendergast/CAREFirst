from fastapi import FastAPI, HTTPException
from typing import List, Dict, Tuple, NamedTuple, Optional
from pydantic import BaseModel, Extra, ValidationError, validator
import os
from datetime import datetime

# Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio

# Mongo
import pymongo
from pymongo import MongoClient

# Model
from src.retrieval_slim import retrieval

app = FastAPI()

# # Redis
# LOCAL_REDIS_URL = "redis://localhost:6379/"

# @app.on_event("startup")
# def startup():
#     HOST_URL = os.environ.get("REDIS_URL", LOCAL_REDIS_URL)
#     redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

class Query(BaseModel, extra='ignore'):
    conversation_id: str
    message_id: str
    question: str

# retrieval function returns: (conversation_id, message_id, page_content, source, timestamp)
class Response(BaseModel):
    output: Tuple[str, str, str, str, datetime]

class Feedback(BaseModel, extra='ignore'):
    conversation_id: str
    message_id: str
    user_feedback: bool

@app.post("/conversations", response_model=Response)
#@cache(expire=60)
async def conversations(text: Query) -> Response:

    # Generate Response
    ai_response = retrieval(text.conversation_id, text.message_id, text.question)

    # Store conversation id, message id, conversation in mongodb database table?

    return {"output": ai_response}

@app.post("/messages")
async def messages(feedback: Feedback):

    # Store feedback in database

    return {"feedback": feedback.user_feedback}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}


