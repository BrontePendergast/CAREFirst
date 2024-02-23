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

class Query(BaseModel, extra='ignore'):
    id: Optional[str] = None
    question: str

class Response(BaseModel):
    output: Tuple[str, str, str, str, datetime]

    def output_to_dict(self):
        # initialize empty dictionary
        output_dict = {}
        keys = ("conversation_id", "message_id", "page_content", "source", "timestamp")
 
        # Using loop to populate the dictionary
        for i in range(len(self)):
            output_dict[keys[i]] = self[i]
        return output_dict

class Feedback(BaseModel, extra='ignore'):
    conversation_id: str
    message_id: str
    user_feedback: bool

#https://stackoverflow.com/questions/69915232/how-to-pass-the-path-parameter-to-the-pydantic-model
@app.post("/conversations/{conversation_id}", response_model=Response)
#@cache(expire=60)
async def conversations(conversation_id, text: Query) -> Response:
    text.id = conversation_id
    # Generate Response
    ai_response = retrieval(text.question, conversation_id)
    # Store conversation id, message id, trimmed conversation in mongodb database table
    # Update "messsage_id" and "trimmed conversation" with every new message
    
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
