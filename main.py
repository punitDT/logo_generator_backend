from routes.generate_logo_routes import generate_logo_router
from routes.edit_logo_routes import edit_logo_router
from config import PORT
from fastapi import FastAPI

app = FastAPI(
    title="AI Logo Generator",
    description="Generate logos from text using Hugging Face Inference API (FLUX.1-dev).",
    version="1.0.0"
)

# Register routes
app.include_router(generate_logo_router, prefix="/api", tags=["Logo Generator"]) # Generate Logo
app.include_router(edit_logo_router, prefix="/api", tags=["Logo Generator"]) # Edit Logo

@app.get("/")
def root():
    return {"message": "🚀 Logo Generator API running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
