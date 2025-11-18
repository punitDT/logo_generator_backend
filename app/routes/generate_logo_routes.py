"""
Logo Generation Routes
API endpoints for generating professional logos
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict
import base64

from app.services.generate_logo_service import generate_logo
from app.config import Config


# Router instance
router = APIRouter()


class LogoRequest(BaseModel):
    """Request model for logo generation"""
    
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Description of the desired logo",
        example="Modern tech startup with AI focus"
    )
    sizes: List[int] = Field(
        default=Config.DEFAULT_SIZES,
        description="List of output sizes in pixels",
        example=[256, 512, 1024]
    )
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt is not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()
    
    @validator('sizes')
    def validate_sizes(cls, v):
        """Validate sizes are within acceptable range"""
        if not v:
            return Config.DEFAULT_SIZES
        
        valid_sizes = [
            size for size in v 
            if Config.MIN_SIZE <= size <= Config.MAX_SIZE
        ]
        
        if not valid_sizes:
            raise ValueError(
                f'All sizes must be between {Config.MIN_SIZE} and {Config.MAX_SIZE}'
            )
        
        return valid_sizes


class LogoResponse(BaseModel):
    """Response model for logo generation"""
    
    message: str
    prompt: str
    images: Dict[str, str]
    sizes: List[int]
    model: str


@router.post(
    "/generate_logo",
    response_model=LogoResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Professional Logo",
    description="Generate a professional logo from a text description using AI"
)
async def generate_logo_endpoint(request: LogoRequest) -> JSONResponse:
    """
    Generate a professional logo from a text prompt.
    
    The API enhances your prompt with professional logo design keywords to ensure
    clean, minimalist, and brand-ready outputs suitable for corporate identity.
    
    Args:
        request: LogoRequest containing prompt and desired sizes
        
    Returns:
        JSON response with base64-encoded images in all requested sizes
        
    Raises:
        HTTPException: If logo generation fails
    """
    
    try:
        # Generate logo with all requested sizes (now async)
        result = await generate_logo(request.prompt, request.sizes)

        # Convert all sizes to base64 for JSON response
        images = {}
        for size, image_bytes in result.items():
            images[str(size)] = base64.b64encode(image_bytes).decode('utf-8')

        return JSONResponse(
            content={
                "message": "Logo generated successfully!",
                "prompt": request.prompt,
                "images": images,
                "sizes": request.sizes,
                "model": Config.get_model_identifier()
            },
            status_code=status.HTTP_200_OK
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate logo: {str(e)}"
        )

