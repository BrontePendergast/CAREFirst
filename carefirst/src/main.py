from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
# from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict

import os
from datetime import datetime
import string
import random


# Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio

# Mongo
import pymongo
from pymongo import MongoClient
from pydantic_mongo import AbstractRepository, ObjectIdField

from src.db_mongo import getURI
from src.llm import *

# MongoDB
connection_string= getURI()
client = pymongo.MongoClient(connection_string)
database = client["carefirstdb"]

class RequestQuery(BaseModel):
    # id: str = ""
    input: str


class Response(BaseModel):
    conversation_id: str
    # message_id: Optional[str] = None
    answer: str
    query: str
    source: str
    #model: str
    timestamp: datetime

    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)

# class MessageRecord(BaseModel):
#     id: ObjectIdField = None
#     conversation_id: str
#     message_id: str
#     answer: str
#     query: str
#     feedback: Optional[bool] = None
#     timestamp_sent_query: datetime
#     timestamp_sent_response: datetime
#     response_duration: datetime

# class MessagesRepository(AbstractRepository[MessageRecord]):
#    class Meta:
#       collection_name = 'messages'

class Feedback(BaseModel):
    #id: Optional[str] = None
    feedback: bool

app = FastAPI()  

def getMessageID():
    # Generate random string of length N
    N = 7
    message_id = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    return message_id


@app.post("/conversations/{conversation_id}")
# @cache(expire=60, coder=PickleCoder)
async def conversations(input: RequestQuery, conversation_id: str):

    # input.id =  conversation_id

    # return {"id" : conversation_id, "output": response}
    
    # # Generate Response
    # timestamp_queryin = datetime.now()
    ai_response = ChatChain(input.input, input.id)
    validated_response = Response(**ai_response)

    # Create message_id
    # message_id = getMessageID()
    # validated_response.update(message_id = message_id)

    # Calculate response duration
    # response_duration = validated_response.timestamp - timestamp_queryin                         
    # duration_in_s = response_duration.total_seconds()
    
    # # Store record in "messages" collection
    # messages_repository = MessagesRepository(database=database)
    # message = MessageRecord(conversation_id = text.id
    #                         , message_id=message_id
    #                         , answer=validated_response.answer
    #                         , query=validated_response.query
    #                         , timestamp_sent_query = timestamp_queryin
    #                         , timestamp_sent_response=validated_response.timestamp
    #                         , response_duration=duration_in_s)

    # messages_repository.save(message)

    # Return Response
    #return validated_response
    return {"output": validated_response}
    # return {"output": response}

@app.post("/messages/{message_id}")
async def messages( user_feedback: Feedback, message_id: str):
    #user_feedback.id = message_id
    
    #Confirm message id exists
    result = database["messages"].find_one({'message_id': message_id}) 
    if result:

        # Update message collection with feedback
        database["messages"].update_one(
                {"message_id": message_id}, 
                {'$set': {"feedback": user_feedback.feedback}})   

        return {"output": user_feedback} 
        #return user_feedback
    
    else:
        return

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}

#Code that Charlie needed to run locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

#Redis
LOCAL_REDIS_URL = "redis://localhost:6379/"

@app.on_event("startup")
def startup():
    HOST_URL = os.environ.get("REDIS_URL", LOCAL_REDIS_URL)
    redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
