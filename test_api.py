"""
Test script for AI Logo Generator API
Run this after starting the server with: python run.py
"""

import requests
import json
import base64
from pathlib import Path

# API Configuration
API_URL = "http://localhost:8003"
GENERATE_ENDPOINT = f"{API_URL}/api/generate_logo"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_generate_logo(prompt: str, sizes: list = None):
    """Test logo generation"""
    if sizes is None:
        sizes = [256, 512]
    
    print(f"🎨 Generating logo with prompt: '{prompt}'")
    print(f"📐 Requested sizes: {sizes}")
    
    payload = {
        "prompt": prompt,
        "sizes": sizes
    }
    
    try:
        response = requests.post(GENERATE_ENDPOINT, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Generated {len(data['images'])} sizes")
            print(f"Model used: {data['model']}")
            
            # Save images to disk
            output_dir = Path("test_outputs")
            output_dir.mkdir(exist_ok=True)
            
            for size, base64_img in data['images'].items():
                # Decode base64 and save
                img_data = base64.b64decode(base64_img)
                filename = output_dir / f"logo_{prompt[:20].replace(' ', '_')}_{size}px.png"
                
                with open(filename, 'wb') as f:
                    f.write(img_data)
                
                print(f"💾 Saved: {filename}")
            
            print()
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}\n")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 AI Logo Generator API Tests")
    print("=" * 60)
    print()
    
    # Test health check
    test_health_check()
    
    # Test logo generation with different prompts
    test_prompts = [
        "Modern tech startup",
        "Coffee shop with mountain theme",
        "Fitness app with lightning bolt",
    ]
    
    for prompt in test_prompts:
        test_generate_logo(prompt, sizes=[256, 512])
    
    print("=" * 60)
    print("✅ Tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

