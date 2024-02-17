from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel, Extra, ValidationError, validator
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio

logger = logging.getLogger(__name__)

# Model
from src.retrieval_slim import retrieval

app = FastAPI()

# Redis
LOCAL_REDIS_URL = "redis://localhost:6379/"

@app.on_event("startup")
def startup():
    HOST_URL = os.environ.get("REDIS_URL", LOCAL_REDIS_URL)
    logger.debug(HOST_URL)
    redis = asyncio.from_url(HOST_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

class Query(BaseModel, extra='ignore'):
    query: str
    
class Retrieved(BaseModel):
    page_content: str

@cache(expire=60)
@app.post("/predict", response_model=Retrieved)
async def predict(query: Query):
    prediction = retrieval(query)
    return {"prediction": prediction}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}

