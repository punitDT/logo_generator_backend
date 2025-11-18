"""
Logo Generation Service
Handles professional logo generation with AI-powered prompt enhancement
Uses local GPU model inference instead of HuggingFace API
"""

from io import BytesIO
from typing import Dict
from PIL import Image
import asyncio
import logging
from app.config import Config
from app.model_manager import ModelManager

logger = logging.getLogger(__name__)


class LogoPromptEnhancer:
    """Enhances user prompts for professional logo generation"""
    
    LOGO_KEYWORDS = [
        "Professional logo design",
        "Clean, minimalist, vector-style graphic",
        "Flat design with bold shapes and clear iconography",
        "Simple color palette, high contrast, suitable for branding",
        "No text, no background, transparent or solid background",
        "Modern, memorable, scalable design",
        "Corporate identity style, professional branding aesthetic",
        "Icon-based design, suitable for app icons and brand marks"
    ]
    
    @classmethod
    def enhance(cls, user_prompt: str) -> str:
        """
        Enhance user prompt with logo-specific keywords
        
        Args:
            user_prompt: Original user prompt
            
        Returns:
            Enhanced prompt optimized for logo generation
        """
        enhanced = f"{user_prompt}. {'. '.join(cls.LOGO_KEYWORDS)}"
        return enhanced


def validate_sizes(sizes: list[int]) -> list[int]:
    """
    Validate and filter requested sizes
    
    Args:
        sizes: List of requested image sizes
        
    Returns:
        Validated list of sizes within acceptable range
    """
    valid_sizes = [
        size for size in sizes 
        if Config.MIN_SIZE <= size <= Config.MAX_SIZE
    ]
    
    if not valid_sizes:
        return Config.DEFAULT_SIZES
    
    return sorted(set(valid_sizes))  # Remove duplicates and sort


async def generate_logo(prompt: str, sizes: list[int] = None) -> Dict[int, bytes]:
    """
    Generate a professional logo from a text prompt using local GPU Flux model.
    Applies logo-specific prompt engineering to ensure clean, professional designs.

    Args:
        prompt: User's description of the desired logo
        sizes: List of output sizes in pixels (default: [256, 512, 1024])

    Returns:
        Dictionary mapping size to PNG image bytes

    Raises:
        ValueError: If model output is invalid
        Exception: For other generation errors
    """

    # Use default sizes if none provided
    if sizes is None:
        sizes = Config.DEFAULT_SIZES

    # Validate sizes
    sizes = validate_sizes(sizes)

    # Enhance prompt for logo generation
    enhanced_prompt = LogoPromptEnhancer.enhance(prompt)

    logger.info(f"🎨 Generating logo for prompt: {prompt}")
    logger.debug(f"📝 Enhanced prompt: {enhanced_prompt[:100]}...")
    logger.info(f"📐 Requested sizes: {sizes}")

    try:
        # Get model manager instance
        model_manager = await ModelManager.get_instance(
            max_concurrent_jobs=Config.MAX_CONCURRENT_JOBS
        )

        # Determine the largest size for initial generation
        max_size = max(sizes)

        # Generate image using local GPU model
        # Use square dimensions for logo generation
        image = await model_manager.generate_image(
            prompt=enhanced_prompt,
            height=max_size,
            width=max_size,
            num_inference_steps=Config.DEFAULT_INFERENCE_STEPS,
            guidance_scale=Config.DEFAULT_GUIDANCE_SCALE
        )

        if not isinstance(image, Image.Image):
            raise ValueError("Model output is not a valid image object.")

        logger.info(f"✅ Base image generated: {image.size}")

        # Generate multiple sizes
        result = {}
        for size in sizes:
            if size == max_size:
                # Use original image for max size
                resized_img = image
            else:
                # Use high-quality LANCZOS resampling for smaller sizes
                resized_img = image.resize((size, size), Image.Resampling.LANCZOS)

            # Convert to PNG bytes
            buffer = BytesIO()
            resized_img.save(buffer, format="PNG", optimize=True)
            buffer.seek(0)
            result[size] = buffer.getvalue()

            logger.info(f"✅ Generated {size}x{size} version")

        return result

    except Exception as e:
        logger.error(f"❌ Error generating logo: {str(e)}", exc_info=True)
        raise

