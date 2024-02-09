from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel, Extra, ValidationError, validator
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache.decorator import cache
# from joblib import load
# #from redis import asyncio as aioredis

from src.retrieval import retrieval

app = FastAPI()

class Query(BaseModel, extra='ignore'):
    query: str
    
class Retrieved(BaseModel):
    page_content: str

@app.post("/predict", response_model=Retrieved)
async def predict(input: Query):
    prediction = retrieval(input)
    return {"prediction": prediction}

@app.get("/health")
async def health():
    return {"status": "healthy"}

#print(retrieval('what cut'))

# test = Query(query='what is burn')
# print(test.text)