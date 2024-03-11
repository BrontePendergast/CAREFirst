from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel, ConfigDict

import os
from datetime import datetime
import string
import random
import numpy as np

# Mongo
import pymongo
from pymongo import MongoClient
from pydantic_mongo import AbstractRepository, ObjectIdField

# LLM
from src.db_mongo import getURI
from src.llm import ChatChain

# Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from fastapi_cache.coder import PickleCoder

# Load the Model once
# model = joblib.load("model_pipeline.pkl")

# Connect to MongoDB
connection_string= getURI()
client = pymongo.MongoClient(connection_string)
database = client["carefirstdb"]

class RequestQuery(BaseModel):
    id: Optional[str] = None
    query: str

class Response(BaseModel):
    message_id: Optional[str] = None
    conversation_id: str
    answer: str
    query: str
    source: str
    model: str
    timestamp: str

    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)

class Feedback(BaseModel):
    id: Optional[str] = None
    feedback: bool

app = FastAPI()

def getMessageID():
    # Generate random string of length N
    N = 7
    message_id = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    return message_id

#Code that Charlie needed to run locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.post(
    "/conversations/{conversation_id}",
    response_model=Response
)
# @cache(expire=60, coder=PickleCoder)
async def predict_value(conversation_id: str, input: RequestQuery) -> Response:
    input.id = conversation_id

    ai_response = ChatChain(input.input, input.id)
    validated_response = Response(**ai_response)
    return {"house_value": input.input}

@app.get(
    "/health",
    summary="Healthcheck endpoint",
    description="Returns HTTP Status 200 with timestamp in ISO8601 format",
)
async def health_check():
    return {"time": f"{datetime.datetime.now().isoformat()}"}

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://redis:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
