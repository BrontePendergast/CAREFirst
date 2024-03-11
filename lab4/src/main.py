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
    model: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)

class Feedback(BaseModel):
    id: Optional[str] = None
    feedback: bool

class ResponseFeedback(BaseModel):
    id: Optional[str] = None
    status: str
    modified_count: int

class MessageRecord(BaseModel):
    id: ObjectIdField = None
    conversation_id: str
    message_id: str
    answer: str
    query: str
    feedback: Optional[bool] = None
    timestamp_sent_query: datetime
    timestamp_sent_response: datetime
    response_duration: float

class MessagesRepository(AbstractRepository[MessageRecord]):
   class Meta:
      collection_name = 'messages'


# Initiate fastapi
app = FastAPI()


# messageID funciton
def getMessageID():
    # Generate random string of length N
    N = 7
    message_id = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    return message_id


#Code that Charlie needed to run locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
                   "http://localhost:8000",
                    "*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Conversations endpoint
@app.post(
    "/conversations/{conversation_id}",
    response_model=Response
)
# @cache(expire=60, coder=PickleCoder)
async def conversations(conversation_id: str, query: RequestQuery) -> Response:
    
    # Set ID to conversation
    query.id = conversation_id


    # Generate Response
    timestamp_queryin = datetime.now()
    ai_response = ChatChain(query.query, query.id)
    validated_response = Response(**ai_response)
    

    # Create message_id
    message_id = getMessageID()
    validated_response.update(message_id = message_id)


    # Calculate response duration
    response_duration = validated_response.timestamp - timestamp_queryin                         
    duration_in_s = response_duration.total_seconds()


    # Store record in "messages" collection
    messages_repository = MessagesRepository(database=database)
    message = MessageRecord(conversation_id = query.id
                            , message_id=message_id
                            , answer=validated_response.answer
                            , query=validated_response.query
                            , timestamp_sent_query = timestamp_queryin
                            , timestamp_sent_response=validated_response.timestamp
                            , response_duration=duration_in_s)
    messages_repository.save(message)


    # Return response
    return validated_response


@app.post(
        "/messages/{message_id}",
        response_model=ResponseFeedback
)
# @cache(expire=60, coder=PickleCoder)
async def messages(feedback: Feedback, message_id: str) -> ResponseFeedback:
    feedback.id = message_id
    
    
    # Update message collection with feedback
    try:    
        update_result = database["messages"].update_one(
            {"message_id": feedback.id}, 
            {'$set': {"feedback": feedback.feedback}})   
        
        if update_result.matched_count < 1:
            # raise HTTPException(status_code=404, detail="Matched count: " + str(update_result.matched_count))
            return {"id":feedback.id,
                "status": "Error",
                "modified_count":update_result.matched_count}
        else:    
            return {"id":feedback.id,
                "status": "Success",
                "modified_count":update_result.modified_count}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error | " + str(e))

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