from io import BytesIO
from PIL import Image
from config import client

def generate_logo(prompt: str, sizes: list[int] = [512]) -> dict:
    """
    Generate a logo from a text prompt using the FLUX.1-dev model.
    Returns multiple PNG sizes.
    """

    print(f"🎨 Generating logo for prompt: {prompt}")

    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-dev",
    )

    if not isinstance(image, Image.Image):
        raise ValueError("Inference output is not a valid image object.")

    result = {}
    for size in sizes:
        resized_img = image.resize((size, size))
        buffer = BytesIO()
        resized_img.save(buffer, format="PNG")
        buffer.seek(0)
        result[size] = buffer.getvalue()

    return result
