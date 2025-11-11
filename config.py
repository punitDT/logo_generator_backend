import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load .env file
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
PORT = int(os.getenv("PORT", 8000))

if not HF_TOKEN:
    raise ValueError("❌ HF_TOKEN is missing from environment variables.")

# Initialize client once
client = InferenceClient(
    provider="nebius",
    api_key=HF_TOKEN,
)

print("✅ Hugging Face Inference Client initialized successfully.")
