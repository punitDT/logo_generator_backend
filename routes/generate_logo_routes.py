from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from services.generate_logo_service import generate_logo

generate_logo_router = APIRouter()

class LogoRequest(BaseModel):
    prompt: str
    sizes: list[int] = [256, 512, 1024]

@generate_logo_router.post("/generate_logo")
async def generate_logo_route(request: LogoRequest):
    try:
        result = generate_logo(request.prompt, request.sizes)
        # Return the largest size as the main preview
        largest_size = max(request.sizes)
        return Response(
            content=result[largest_size],
            media_type="image/png",
            headers={"X-Generated-By": "FLUX.1-dev via HuggingFace"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
