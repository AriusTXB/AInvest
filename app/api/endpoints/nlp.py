from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.nlp_service import nlp_service

router = APIRouter()

class SentimentRequest(BaseModel):
    text: str

@router.post("/analyze")
async def analyze_text(request: SentimentRequest):
    """
    Analyze financial text sentiment.
    """
    result = nlp_service.analyze_sentiment(request.text)
    return result
