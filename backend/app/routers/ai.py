"""AI-powered routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..services import AIService
from ..schemas import BriefRequest, BriefResponse, InsightsRequest, InsightsResponse
from ..exceptions import AIError
from ..middleware.auth import require_auth
from ..models import User

router = APIRouter(prefix="/ai", tags=["AI"])


def get_ai_service() -> AIService:
    return AIService()


@router.post("/brief", response_model=BriefResponse)
async def generate_brief(
    request: BriefRequest,
    current_user: User = Depends(require_auth()),
    service: AIService = Depends(get_ai_service),
):
    try:
        result = service.generate_brief(
            name=request.name,
            target_audience=request.target_audience,
            budget=request.budget,
            currency=request.currency,
        )
        return result
    except AIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unavailable: {e.message}"
        )


@router.post("/insights", response_model=InsightsResponse)
async def generate_insights(
    request: InsightsRequest,
    current_user: User = Depends(require_auth()),
    service: AIService = Depends(get_ai_service),
):
    try:
        result = service.generate_insights(request.campaigns)
        return {"insights": result}
    except AIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unavailable: {e.message}"
        )
