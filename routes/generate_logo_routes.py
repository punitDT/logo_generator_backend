from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.generate_logo_service import generate_logo
import base64

generate_logo_router = APIRouter()

class LogoRequest(BaseModel):
    prompt: str
    sizes: list[int] = [256, 512, 1024]

@generate_logo_router.post("/generate_logo")
async def generate_logo_route(request: LogoRequest):
    """
    Generate a professional logo from a text prompt.
    Returns all requested sizes as base64-encoded images.
    """
    try:
        result = generate_logo(request.prompt, request.sizes)

        # Convert all sizes to base64 for JSON response
        images = {}
        for size, image_bytes in result.items():
            images[str(size)] = base64.b64encode(image_bytes).decode('utf-8')

        return JSONResponse({
            "message": "Logo generated successfully!",
            "prompt": request.prompt,
            "images": images,
            "sizes": request.sizes,
            "model": "FLUX.1-dev"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
