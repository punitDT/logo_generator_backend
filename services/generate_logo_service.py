from io import BytesIO
from PIL import Image
from config import client

def generate_logo(prompt: str, sizes: list[int] = [512]) -> dict:
    """
    Generate a professional logo from a text prompt using the FLUX.1-dev model.
    Applies logo-specific prompt engineering to ensure clean, professional designs.
    Returns multiple PNG sizes.
    """

    # Enhanced prompt engineering for logo generation
    logo_prompt = f"""Professional logo design: {prompt}.
Clean, minimalist, vector-style graphic.
Flat design with bold shapes and clear iconography.
Simple color palette, high contrast, suitable for branding.
No text, no background, transparent or solid background.
Modern, memorable, scalable design.
Corporate identity style, professional branding aesthetic."""

    print(f"🎨 Generating logo for prompt: {prompt}")
    print(f"📝 Enhanced prompt: {logo_prompt}")

    image = client.text_to_image(
        logo_prompt,
        model="black-forest-labs/FLUX.1-dev",
    )

    if not isinstance(image, Image.Image):
        raise ValueError("Inference output is not a valid image object.")

    result = {}
    for size in sizes:
        resized_img = image.resize((size, size), Image.Resampling.LANCZOS)
        buffer = BytesIO()
        resized_img.save(buffer, format="PNG")
        buffer.seek(0)
        result[size] = buffer.getvalue()

    return result
