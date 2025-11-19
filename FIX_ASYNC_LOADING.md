# Fix: Async Model Loading to Prevent Startup Hang

## Problem
The application was hanging during startup when loading the FLUX.1-dev model. The logs showed:
```
Loading checkpoint shards: 100%|████████| 2/2 [00:21<00:00, 10.61s/it]
Loading pipeline components...: 57%|█████| 4/7 [00:21<00:15, 5.30s/it]
Loading checkpoint shards: 33%|█████| 1/3 [00:29<00:59, 29.57s/it]
```

The app was stuck because the model loading operations were blocking the asyncio event loop.

## Root Cause
The `FluxPipeline.from_pretrained()` and `pipeline.to(device)` operations are CPU-bound synchronous operations that:
1. Download large model files from HuggingFace (if not cached)
2. Load checkpoint shards from disk
3. Move tensors to GPU memory

These operations were running directly in the async event loop, blocking all other async operations.

## Solution
Modified `app/model_manager.py` to run all blocking operations in a ThreadPoolExecutor:

### Changes Made:

1. **Added ThreadPoolExecutor**
   - Import: `from concurrent.futures import ThreadPoolExecutor`
   - Created executor in `__init__`: `self.executor = ThreadPoolExecutor(max_workers=1)`

2. **Split Model Loading into Sync/Async Parts**
   - Created `_load_model_sync()`: Synchronous function that runs in thread pool
   - Modified `load_model()`: Now runs blocking operations via `loop.run_in_executor()`
   - Operations moved to executor:
     - `FluxPipeline.from_pretrained()` - Downloads and loads model
     - `pipeline.to(device)` - Moves model to GPU

3. **Updated Image Generation**
   - Created `_generate_image_sync()`: Synchronous inference function
   - Modified `generate_image()`: Runs inference via executor
   - Prevents blocking during image generation

4. **Updated Warmup**
   - Modified `warmup()`: Runs warmup inference via executor
   - Prevents blocking during GPU warmup

5. **Updated Cleanup**
   - Modified `cleanup()`: Properly shuts down thread pool executor

## Benefits

✅ **Non-blocking Startup**: App can respond to health checks while model loads
✅ **Better Logging**: Progress messages appear in real-time
✅ **Concurrent Operations**: Event loop remains responsive
✅ **Proper Resource Management**: Thread pool is properly cleaned up

## Technical Details

### Before (Blocking):
```python
self.pipeline = FluxPipeline.from_pretrained(...)  # Blocks event loop
self.pipeline = self.pipeline.to(self.device)      # Blocks event loop
```

### After (Non-blocking):
```python
loop = asyncio.get_event_loop()
self.pipeline = await loop.run_in_executor(
    self.executor,
    self._load_model_sync,
    model_name,
    dtype
)
self.pipeline = await loop.run_in_executor(
    self.executor,
    lambda: self.pipeline.to(self.device)
)
```

## Testing
To verify the fix works:
1. Start the server: `python run.py`
2. Model loading should show progress without hanging
3. Server should remain responsive during loading
4. Check logs for proper progress messages

## Notes
- The ThreadPoolExecutor uses only 1 worker since model operations are GPU-bound
- All blocking operations now run in the thread pool
- The event loop remains free to handle other async tasks
- This pattern follows asyncio best practices for CPU-bound operations

