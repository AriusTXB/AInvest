from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.vision_service import vision_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/extract")
async def extract_table(file: UploadFile = File(...)):
    """
    Upload a PDF Financial Report.
    Returns extracted Balance Sheet data.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    content = await file.read()
    result = vision_service.extract_from_pdf(content)
    
    return result
