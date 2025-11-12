"""
Logo Generation Service
Handles professional logo generation with AI-powered prompt enhancement
"""

from io import BytesIO
from typing import Dict
from PIL import Image
from app.config import client, Config


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


def generate_logo(prompt: str, sizes: list[int] = None) -> Dict[int, bytes]:
    """
    Generate a professional logo from a text prompt using FLUX.1-dev model.
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
    
    print(f"🎨 Generating logo for prompt: {prompt}")
    print(f"📝 Enhanced prompt: {enhanced_prompt[:100]}...")
    print(f"📐 Requested sizes: {sizes}")
    
    try:
        # Generate image using FLUX.1-dev model
        image = client.text_to_image(
            enhanced_prompt,
            model=Config.MODEL_NAME,
        )
        
        if not isinstance(image, Image.Image):
            raise ValueError("Model output is not a valid image object.")
        
        print(f"✅ Base image generated: {image.size}")
        
        # Generate multiple sizes
        result = {}
        for size in sizes:
            # Use high-quality LANCZOS resampling
            resized_img = image.resize((size, size), Image.Resampling.LANCZOS)
            
            # Convert to PNG bytes
            buffer = BytesIO()
            resized_img.save(buffer, format="PNG", optimize=True)
            buffer.seek(0)
            result[size] = buffer.getvalue()
            
            print(f"✅ Generated {size}x{size} version")
        
        return result
        
    except Exception as e:
        print(f"❌ Error generating logo: {str(e)}")
        raise

