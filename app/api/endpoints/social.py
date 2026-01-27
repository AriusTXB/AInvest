from fastapi import APIRouter
from app.services.social_service import social_service

router = APIRouter()

@router.get("/feed")
async def get_social_feed():
    """
    Get the latest 'Smart Money' social feed.
    """
    return social_service.get_social_feed()
