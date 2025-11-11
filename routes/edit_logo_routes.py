from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
import base64
from io import BytesIO
from PIL import Image
from services.edit_logo_service import edit_logo

edit_logo_router = APIRouter()

@edit_logo_router.post("/edit_logo")
async def edit_logo_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    """
    Edit an existing logo using a natural language prompt.
    Example: 'Change color to gold and black' or 'Add AI circuit details around the brain'.
    """

    try:
        # ✅ Read uploaded image
        contents = await file.read()
        existing_logo = Image.open(BytesIO(contents)).convert("RGBA")

        print(f"🖌️ Editing logo with prompt: {prompt}")

        # ✅ Generate edited image using image-to-image model
        edited_image = edit_logo(
            existing_logo=existing_logo,
            edit_prompt=prompt,
        )

        if not isinstance(edited_image, Image.Image):
            raise ValueError("Model output is not a valid image object.")

        # ✅ Convert edited image to base64 for API response
        buffer = BytesIO()
        edited_image.save(buffer, format="PNG")
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return JSONResponse({
            "message": "Logo edited successfully!",
            "prompt_used": prompt,
            "image_base64": encoded_image
        })

    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)
