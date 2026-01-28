from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.nlp_service import nlp_service

router = APIRouter()

class SentimentRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str

@router.post("/analyze")
async def analyze_text(request: SentimentRequest):
    """
    Analyze financial text sentiment.
    """
    result = nlp_service.analyze_sentiment(request.text)
    return result

@router.post("/summarize-url")
async def summarize_url(request: URLRequest):
    """
    Scrape and summarize an article from a URL.
    """
    result = nlp_service.summarize_article(request.url)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result
