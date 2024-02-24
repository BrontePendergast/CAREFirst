from fastapi import FastAPI, HTTPException
from typing import List, Dict, Tuple, NamedTuple, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Extra, ValidationError, validator, TypeAdapter
from pydantic_mongo import AbstractRepository, ObjectIdField

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
from src.llm_js import ChatChain
#from llm_js import ChatChain

# MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["carefirstdb"]

app = FastAPI()

class Query(BaseModel, extra='ignore'):
    id: Optional[str] = None
    question: str

class Response(BaseModel):
    output: Tuple[str, str, str, str, str, str, str, datetime]

class History(BaseModel):
    id: ObjectIdField = None
    conversation_id: str
    message_id: int
    new_history_human: str
    new_history_ai: str
    timestamp: datetime

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        return data

    def __getitem__(self, item):
        return getattr(self, item)

class HistoryRepository(AbstractRepository[History]):
   class Meta:
      collection_name = 'history'

# class Response(BaseModel):
#     conversation_id: str
#     message_id: str
#     answer: str
#     history: str
#     question: str
#     source: str
#     timestamp: datetime

class Feedback(BaseModel, extra='ignore'):
    conversation_id: str
    message_id: str
    user_feedback: bool

def getHistory(conversation_id):
    result = database["history"].find_one({'conversation_id': conversation_id})
    if not result:
        history_human = ''
        history_ai = ''

    else:
        history_human = result["new_history_human"]
        history_ai = result["new_history_ai"]

    return history_human, history_ai
    
def getMessageID(conversation_id):
    result = database["history"].find_one({'conversation_id': conversation_id})
    if not result:
        message_id = 0
    else:
        message_id = result["message_id"]
        message_id += 1

    return message_id

def setHistory(conversation_id, ai_response):
        message_id = getMessageID(conversation_id=conversation_id)
        history_update = History(conversation_id=conversation_id, message_id=message_id, new_history_human=ai_response[3], new_history_ai=ai_response[4], timestamp=ai_response[6])
    
        database["history"].update_one(
            {'conversation_id': history_update.conversation_id}, 
            {'$set': {"message_id": message_id, "history": history_update.history, "timestamp": history_update.timestamp}}, upsert=True)   

        return

@app.post("/conversations/{conversation_id}", response_model=Response)
#@cache(expire=60)
async def conversations(conversation_id, text: Query) -> TypeAdapter(Response):
    text.id = conversation_id

    # Get conversation history


    # Generate Response
    ai_response = ChatChain(text.question, text.id)  
        
    # Store conversation id, updated conversation history, timestamp in mongodb
    setHistory(conversation_id, ai_response)
    
    # Return Response
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

history_repository = HistoryRepository(database=database)
# result = history_repository.find_one({'conversation_id': history_update.conversation_id})
# print(result)
result = history_repository.find_one_by({'conversation_id': '500'})


# # Redis
# LOCAL_REDIS_URL = "redis://localhost:6379/"

# @app.on_event("startup")
# def startup():
#     HOST_URL = os.environ.get("REDIS_URL", LOCAL_REDIS_URL)
#     redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


# class ResponseTuple:
#     output: Response(BaseModel)
# # retrieval function returns: (conversation_id, message_id, page_content, source, timestamp)
# class Response(BaseModel):
#     output: Tuple[str, str, str, str, datetime]



# class Response(NamedTuple):
#     conversation_id: str
#     message_id: str
#     page_content: str
#     source: str
#     timestamp: datetime

