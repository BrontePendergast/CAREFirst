from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, field_validator, Field, ConfigDict
import joblib

import os
from datetime import datetime
import string
import random
import numpy as np
import datetime

# Mongo
import pymongo
from pymongo import MongoClient
from pydantic_mongo import AbstractRepository, ObjectIdField

# LLM
from src.db_mongo import getURI
# from src.llm import *

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
    input: str

class Response(BaseModel):
    conversation_id: str
    # message_id: Optional[str] = None
    answer: str
    query: str
    source: str
    #model: str
    # timestamp: datetime

    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)


app = FastAPI()

@app.post(
    "/conversations/{conversation_id}",
    response_model=Response
)
# @cache(expire=60, coder=PickleCoder)
async def predict_value(input: RequestQuery) -> Response:
    
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
