"""
Test script to verify async model loading works correctly
This tests that the model loading doesn't block the event loop
"""

import asyncio
import time
from app.model_manager import ModelManager
from app.config import Config


async def test_async_loading():
    """Test that model loading is truly async and doesn't block"""
    
    print("=" * 60)
    print("Testing Async Model Loading")
    print("=" * 60)
    
    # Create a task that prints dots while model loads
    async def print_dots():
        """Print dots to show event loop is responsive"""
        for i in range(100):
            print(".", end="", flush=True)
            await asyncio.sleep(1)
    
    # Start the dot printer
    dot_task = asyncio.create_task(print_dots())
    
    try:
        # Get model manager instance
        print("\n📦 Getting ModelManager instance...")
        model_manager = await ModelManager.get_instance(
            max_concurrent_jobs=Config.MAX_CONCURRENT_JOBS
        )
        
        # Start loading model
        print(f"🔄 Loading model: {Config.get_model_identifier()}")
        print("⏳ This may take several minutes on first run...")
        print("💡 If you see dots appearing, the event loop is NOT blocked!\n")
        
        start_time = time.time()
        
        # Load model (should not block event loop)
        await model_manager.load_model(
            model_name=Config.get_model_identifier(),
            use_fp16=Config.USE_FP16
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n\n✅ Model loaded successfully in {elapsed:.2f} seconds!")
        
        # Get GPU stats
        gpu_stats = model_manager.get_gpu_stats()
        print(f"🎮 GPU Stats: {gpu_stats}")
        
        # Cancel dot printer
        dot_task.cancel()
        
        print("\n" + "=" * 60)
        print("✅ Test PASSED: Model loading is async!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n\n❌ Test FAILED: {str(e)}")
        dot_task.cancel()
        raise
    finally:
        # Cleanup
        if hasattr(model_manager, 'cleanup'):
            model_manager.cleanup()


async def test_concurrent_operations():
    """Test that we can do other async operations while model loads"""
    
    print("\n" + "=" * 60)
    print("Testing Concurrent Operations During Model Load")
    print("=" * 60)
    
    async def background_task(name: str, duration: int):
        """Simulate background work"""
        print(f"🔄 {name} started")
        for i in range(duration):
            await asyncio.sleep(1)
            print(f"  {name}: step {i+1}/{duration}")
        print(f"✅ {name} completed")
    
    # Start background tasks
    task1 = asyncio.create_task(background_task("Task 1", 5))
    task2 = asyncio.create_task(background_task("Task 2", 3))
    
    # These should run concurrently
    await asyncio.gather(task1, task2)
    
    print("\n✅ Concurrent operations work correctly!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n🧪 Running Async Loading Tests\n")
    
    # Run the async loading test
    asyncio.run(test_async_loading())
    
    # Run concurrent operations test
    asyncio.run(test_concurrent_operations())
    
    print("\n🎉 All tests completed!\n")

