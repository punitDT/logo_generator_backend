"""
Test script for AI Logo Generator API (GPU Edition)
Tests the GPU-based inference backend
"""

import requests
import json
import base64
from pathlib import Path
import time

# API Configuration
API_URL = "http://localhost:7860"
HEALTH_ENDPOINT = f"{API_URL}/health"
GENERATE_ENDPOINT = f"{API_URL}/api/generate_logo"


def test_health_check():
    """Test health check endpoint with GPU stats"""
    print("=" * 60)
    print("🔍 Testing health check...")
    print("=" * 60)
    
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data.get('status')}")
            print(f"🤖 Model: {data.get('model')}")
            print(f"📦 Model Loaded: {data.get('model_loaded')}")
            
            if 'gpu' in data:
                gpu = data['gpu']
                print(f"\n🎮 GPU Information:")
                print(f"  Device: {gpu.get('device_name', 'N/A')}")
                print(f"  Memory Allocated: {gpu.get('memory_allocated_gb', 0):.2f} GB")
                print(f"  Memory Total: {gpu.get('memory_total_gb', 0):.2f} GB")
            
            print(f"\n🌍 Environment: {data.get('environment')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        print(f"Make sure the server is running at {API_URL}")
        return False


def test_logo_generation(prompt: str, sizes: list[int] = None):
    """Test logo generation endpoint"""
    if sizes is None:
        sizes = [512]
    
    print("\n" + "=" * 60)
    print(f"🎨 Testing logo generation...")
    print("=" * 60)
    print(f"Prompt: {prompt}")
    print(f"Sizes: {sizes}")
    
    payload = {
        "prompt": prompt,
        "sizes": sizes
    }
    
    try:
        print("\n⏳ Sending request (this may take 10-30 seconds)...")
        start_time = time.time()
        
        response = requests.post(
            GENERATE_ENDPOINT,
            json=payload,
            timeout=300  # 5 minute timeout
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Generated in {elapsed_time:.2f} seconds")
            print(f"Model used: {data.get('model')}")
            print(f"Generated {len(data.get('images', {}))} size(s)")
            
            # Save images to disk
            output_dir = Path("test_outputs_gpu")
            output_dir.mkdir(exist_ok=True)
            
            for size, base64_img in data.get('images', {}).items():
                # Decode base64 and save
                img_data = base64.b64decode(base64_img)
                safe_prompt = prompt[:30].replace(' ', '_').replace('/', '_')
                filename = output_dir / f"logo_{safe_prompt}_{size}px.png"
                
                with open(filename, 'wb') as f:
                    f.write(img_data)
                
                print(f"💾 Saved: {filename} ({len(img_data) / 1024:.1f} KB)")
            
            print(f"\n⚡ Performance: {elapsed_time / len(sizes):.2f}s per size")
            return True
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n❌ Request timeout (>300s)")
        print("The server might be loading the model for the first time.")
        print("Try again in a few minutes.")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error: {str(e)}")
        return False


def test_concurrent_requests():
    """Test multiple concurrent requests"""
    print("\n" + "=" * 60)
    print("🔄 Testing concurrent requests...")
    print("=" * 60)
    
    import concurrent.futures
    
    prompts = [
        "Minimalist tech startup logo",
        "Creative design agency logo",
        "Modern coffee shop logo"
    ]
    
    print(f"Sending {len(prompts)} concurrent requests...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(test_logo_generation, prompt, [256])
            for prompt in prompts
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    elapsed_time = time.time() - start_time
    success_count = sum(results)
    
    print(f"\n📊 Results:")
    print(f"  Total time: {elapsed_time:.2f}s")
    print(f"  Successful: {success_count}/{len(prompts)}")
    print(f"  Average: {elapsed_time / len(prompts):.2f}s per request")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 AI Logo Generator GPU API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Stopping tests.")
        return
    
    # Test 2: Single generation
    test_logo_generation("Modern AI startup logo", [256, 512])
    
    # Test 3: Different prompt
    test_logo_generation("Elegant fashion brand logo", [512])
    
    # Test 4: Concurrent requests (optional)
    try:
        user_input = input("\n🔄 Test concurrent requests? (y/n): ")
        if user_input.lower() == 'y':
            test_concurrent_requests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

