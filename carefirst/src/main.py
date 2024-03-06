from fastapi import FastAPI, HTTPException
from typing import Dict, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Extra, ValidationError, validator, ConfigDict

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

# Model
from src.llm_js import ChatChain
#from llm_js import ChatChain

from src.db_mongo import getURI
#from db_mongo import getURI

# MongoDB
connection_string= getURI()
client = pymongo.MongoClient(connection_string)
database = client["carefirstdb"]

app = FastAPI()

class Query(BaseModel, extra='ignore'):
    id: Optional[str] = None
    query: str

class Response(BaseModel):
    conversation_id: str
    message_id: Optional[str] = None
    answer: str
    query: str
    source: dict
    #model: str
    timestamp_responseout: datetime

    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)

class MessageRecord(BaseModel):
    id: ObjectIdField = None
    conversation_id: str
    message_id: str
    answer: str
    query: str
    feedback: Optional[bool] = None
    timestamp_sent_query: datetime
    timestamp_sent_response: datetime
    response_duration: datetime

class MessagesRepository(AbstractRepository[MessageRecord]):
   class Meta:
      collection_name = 'messages'

class Feedback(BaseModel, extra='ignore'):
    #id: Optional[str] = None
    feedback: bool
  
def getMessageID():

    # size of string
    N = 7
 
    # random string
    message_id = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    return message_id

@app.post("/conversations/{conversation_id}")
@cache(expire=60)
async def conversations(conversation_id, text: Query):

    text.id = conversation_id
    
    # # Generate Response
    timestamp_queryin = datetime.now()
    ai_response = ChatChain(text.query, text.id)
    validated_response = Response(**ai_response)

    # Create message_id
    message_id = getMessageID()
    validated_response.update(message_id = message_id)

    # Calculate response duration
    response_duration = validated_response.timestamp_responseout - timestamp_queryin                         
    duration_in_s = response_duration.total_seconds()
    
    # # Store record in "messages" collection
    messages_repository = MessagesRepository(database=database)
    message = MessageRecord(conversation_id = text.id
                            , message_id=message_id
                            , answer=validated_response.answer
                            , query=validated_response.query
                            , timestamp_sent_query = timestamp_queryin
                            , timestamp_sent_response=validated_response.timestamp_responseout
                            , response_duration=duration_in_s)

    messages_repository.save(message)

    # Return Response
    return {"output": validated_response}

@app.post("/messages/{message_id}")
async def messages(message_id, user_feedback: Feedback):
    #user_feedback.id = message_id
    
    #Confirm message id exists
    result = database["messages"].find_one({'message_id': message_id}) 
    if result:

        # Update message collection with feedback
        database["messages"].update_one(
                {"message_id": message_id}, 
                {'$set': {"feedback": user_feedback.feedback}})   

        return {"output": user_feedback} 
    
    else:
        return

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}



#Redis
LOCAL_REDIS_URL = "redis://localhost:6379/"

@app.on_event("startup")
def startup():
    HOST_URL = os.environ.get("REDIS_URL", LOCAL_REDIS_URL)
    redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")