from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel, Extra, ValidationError, validator

# Model
from src.retrieval_slim import retrieval

app = FastAPI()

class Query(BaseModel, extra='ignore'):
    query: str
    
class Retrieved(BaseModel):
    page_content: str

@app.post("/predict", response_model=Retrieved)
async def predict(query: Query):
    prediction = retrieval(query)
    return {"prediction": prediction}

@app.get("/health")
async def health():
    return {"status": "healthy"}
