from fastapi import FastAPI, HTTPException
from typing import List, Dict, Tuple, NamedTuple, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Extra, ValidationError, validator, TypeAdapter

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
from pydantic_mongo import AbstractRepository, ObjectIdField
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

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
    question: str

class Response(BaseModel):
    output: Tuple[str, str, str, str, str, str, datetime]

class Message(BaseModel):
    id: ObjectIdField = None
    conversation_id: str
    message_id: int
    message_human: str
    message_ai: str
    feedback: Optional[bool] = None
    timestamp: datetime

class MessagesRepository(AbstractRepository[Message]):
   class Meta:
      collection_name = 'messages'

class Feedback(BaseModel, extra='ignore'):
    id: Optional[str] = None
    message_id: int
    user_feedback: bool
  
def getMessageID(conversation_id):
    '''Increment message_id by 1 with each new message in the chat'''
    result = database["messages"].find_one({'conversation_id': conversation_id})
    if not result:
        message_id = 0
    else:
        message_id = result["message_id"]
        message_id += 1

    return message_id

@app.post("/conversations/{conversation_id}", response_model=Response)
#@cache(expire=60)
async def conversations(conversation_id, text: Query) -> TypeAdapter(Response):
    text.id = conversation_id

    # Generate Response
    ai_response = ChatChain(text.question, text.id)  

    # Create message_id
    message_id = getMessageID(conversation_id=text.id)

    # Store record in "messages" collection
    messages_repository = MessagesRepository(database=database)
    message = Message(conversation_id = text.id, message_id=message_id, message_human=ai_response[2], message_ai=ai_response[3], timestamp=ai_response[6])
    messages_repository.save(message)

    # Return Response
    #output_dict = Response(**ai_response)
    return {"output": ai_response}

@app.post("/messages/{conversation_id}")
async def messages(conversation_id, feedback: Feedback):
    feedback.id = conversation_id

    # Update message collection with feedback
    database["messages"].update_one(
            {'conversation_id': feedback.id, "message_id": feedback.message_id}, 
            {'$set': {"feedback": feedback.user_feedback}})   

    return {"output": feedback} 


@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}

# # Redis
# LOCAL_REDIS_URL = "redis://localhost:6379/"

# @app.on_event("startup")
# def startup():
#     HOST_URL = os.environ.get("REDIS_URL", LOCAL_REDIS_URL)
#     redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


# class Response(BaseModel):
#     conversation_id: str
#     answer: str
#     history_human: str
#     history_ai: str
#     question: str
#     source: str
#     timestamp: datetime