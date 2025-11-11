from io import BytesIO
from PIL import Image
from config import client

def edit_logo(existing_logo: Image.Image, edit_prompt: str, sizes: list[int] = [512]) -> dict:
    """
    Edit an existing logo image using a text prompt and the FLUX.1-dev model.
    Users can describe what they want to change using natural language.
    Returns edited logo images in multiple PNG sizes.
    """

    print(f"🖌️ Editing logo with prompt: {edit_prompt}")

    # Send both image and text prompt to model
    edited_image = client.image_to_image(
        image=existing_logo,
        prompt=edit_prompt,
        model="black-forest-labs/FLUX.1-dev",
        strength=0.7  # controls how much change occurs; 1.0 = complete redesign
    )

    if not isinstance(edited_image, Image.Image):
        raise ValueError("Model output is not a valid image object.")

    result = {}
    for size in sizes:
        resized_img = edited_image.resize((size, size))
        buffer = BytesIO()
        resized_img.save(buffer, format="PNG")
        buffer.seek(0)
        result[size] = buffer.getvalue()

    return result
