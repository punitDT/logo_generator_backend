# 🎨 AI Logo Generator

Professional logo generation API powered by FLUX.1-dev model via Hugging Face.

## ✨ Features

- **Professional Logo Generation**: AI-powered logo creation with automatic prompt enhancement
- **Multiple Sizes**: Generate logos in multiple sizes (256x256, 512x512, 1024x1024)
- **Logo-Specific Optimization**: Automatic prompt engineering for clean, minimalist, brand-ready designs
- **RESTful API**: Easy-to-use FastAPI endpoints with automatic documentation
- **Base64 Output**: Returns images in base64 format for easy integration

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Hugging Face API Token

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```env
HF_TOKEN=your_huggingface_token_here
PORT=8003
```

### Running the Server

```bash
python run.py
```

The server will start at `http://localhost:8003`

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

### Generate Logo Endpoint

**POST** `/api/generate_logo`

**Request Body:**
```json
{
  "prompt": "Modern tech startup with AI focus",
  "sizes": [256, 512, 1024]
}
```

**Response:**
```json
{
  "message": "Logo generated successfully!",
  "prompt": "Modern tech startup with AI focus",
  "images": {
    "256": "base64_encoded_image...",
    "512": "base64_encoded_image...",
    "1024": "base64_encoded_image..."
  },
  "sizes": [256, 512, 1024],
  "model": "black-forest-labs/FLUX.1-dev"
}
```

## 🏗️ Project Structure

```
logo_generator_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration & settings
│   ├── routes/
│   │   ├── __init__.py
│   │   └── generate_logo_routes.py
│   └── services/
│       ├── __init__.py
│       └── generate_logo_service.py
├── run.py                   # Application entry point
├── requirements.txt
├── .env
└── README.md
```

## 🎯 How It Works

1. **Prompt Enhancement**: User prompts are automatically enhanced with professional logo design keywords
2. **AI Generation**: FLUX.1-dev model generates high-quality logo images
3. **Multi-Size Output**: Images are resized to requested dimensions using high-quality LANCZOS resampling
4. **Base64 Encoding**: All images are returned as base64 strings for easy integration

## 🔧 Configuration

Edit `app/config.py` to customize:
- Default sizes
- Model settings
- Size constraints (min/max)

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

