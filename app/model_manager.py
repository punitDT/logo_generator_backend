"""
Model Manager for Local GPU Flux Inference
Handles model loading, GPU management, and image generation
"""

import torch
import asyncio
from typing import Optional
from PIL import Image
from io import BytesIO
from diffusers import FluxPipeline
import logging
from concurrent.futures import ThreadPoolExecutor
import psutil
import os

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Singleton model manager for Flux model inference on GPU.
    Handles model loading, GPU memory management, and concurrent inference.
    """
    
    _instance: Optional['ModelManager'] = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        """Initialize model manager (use get_instance() instead)"""
        self.pipeline: Optional[FluxPipeline] = None
        # Detect best available device: CUDA > MPS > CPU
        if torch.cuda.is_available():
            self.device: str = "cuda"
        elif torch.backends.mps.is_available():
            self.device: str = "mps"
        else:
            self.device: str = "cpu"
        self.model_loaded: bool = False
        self.semaphore: Optional[asyncio.Semaphore] = None
        # Thread pool for CPU-bound operations (model loading)
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        
    @classmethod
    async def get_instance(cls, max_concurrent_jobs: int = 2) -> 'ModelManager':
        """
        Get or create singleton instance of ModelManager.
        
        Args:
            max_concurrent_jobs: Maximum number of concurrent inference jobs
            
        Returns:
            ModelManager instance
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls._instance.semaphore = asyncio.Semaphore(max_concurrent_jobs)
        return cls._instance
    
    def _load_model_sync(self, model_name: str, dtype: torch.dtype, device: str) -> FluxPipeline:
        """
        Synchronous model loading function to run in thread pool.

        Args:
            model_name: HuggingFace model name or local path
            dtype: Torch dtype for model precision
            device: Target device (cuda, mps, cpu)

        Returns:
            Loaded FluxPipeline
        """
        # Check available system memory
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        logger.info(f"💾 Available System Memory: {available_memory_gb:.2f} GB")

        if available_memory_gb < 30:
            logger.error(f"❌ CRITICAL: Only {available_memory_gb:.2f} GB RAM available")
            logger.error("❌ FLUX.1-dev requires ~30GB+ RAM to load")
            logger.error("❌ Please close other applications to free up memory")
            logger.error("❌ Or use a smaller model like FLUX.1-schnell")
            raise RuntimeError(
                f"Insufficient memory: {available_memory_gb:.2f} GB available, "
                f"but ~30GB+ required for FLUX.1-dev. "
                f"Please close other applications or use a smaller model."
            )

        logger.info("📥 Loading model from cache/HuggingFace...")
        logger.info("⏳ Large model (~24GB) - loading into memory may take 5-10 minutes...")
        logger.info("💡 This is normal - the model is being loaded into RAM then moved to GPU")

        # Set environment variable to reduce memory fragmentation on MPS
        if device == "mps":
            os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
            logger.info("🔧 MPS memory optimization enabled")

        # This is the blocking operation that downloads and loads the model
        # Using 'dtype' instead of deprecated 'torch_dtype'
        # Load directly to device to avoid double memory usage
        pipeline = FluxPipeline.from_pretrained(
            model_name,
            torch_dtype=dtype,  # Keep torch_dtype for compatibility
            use_safetensors=True,
            device_map=None,  # Don't use device_map, we'll move manually
            low_cpu_mem_usage=True  # Reduce CPU memory usage during loading
        )

        logger.info("✅ Model loaded from disk into CPU memory")

        # Check memory again after loading
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        logger.info(f"💾 Available Memory After Load: {available_memory_gb:.2f} GB")

        logger.info(f"🔄 Moving model to {device.upper()}... (this may take 2-5 minutes)")

        # Move to target device
        pipeline = pipeline.to(device)

        logger.info(f"✅ Model successfully moved to {device.upper()}")
        return pipeline

    async def load_model(self, model_name: str, use_fp16: bool = True) -> None:
        """
        Load Flux model into GPU memory asynchronously.

        Args:
            model_name: HuggingFace model name or local path
            use_fp16: Use FP16 precision for faster inference

        Raises:
            RuntimeError: If GPU is not available or model loading fails
        """
        if self.model_loaded:
            logger.info("Model already loaded, skipping...")
            return

        # Check for GPU availability (CUDA or MPS)
        if not (torch.cuda.is_available() or torch.backends.mps.is_available()):
            raise RuntimeError("No GPU acceleration available. This backend requires CUDA or MPS support.")

        logger.info(f"Loading Flux model: {model_name}")
        logger.info(f"Device: {self.device}")

        # Log device-specific information
        if torch.cuda.is_available():
            logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
            logger.info(f"Available GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        elif torch.backends.mps.is_available():
            logger.info(f"MPS Device: Apple Silicon GPU")
            logger.info(f"Memory: Shared with system RAM")

        try:
            # Determine dtype
            # Note: MPS doesn't support float16 as well as CUDA, use float32 for MPS
            if self.device == "mps" and use_fp16:
                logger.warning("MPS doesn't fully support FP16, using FP32 instead")
                dtype = torch.float32
            else:
                dtype = torch.float16 if use_fp16 else torch.float32

            # Run the blocking model loading in a thread pool to avoid blocking the event loop
            # This now includes moving to device, so we don't need a separate step
            loop = asyncio.get_event_loop()
            self.pipeline = await loop.run_in_executor(
                self.executor,
                self._load_model_sync,
                model_name,
                dtype,
                self.device
            )

            # Enable memory optimizations (CUDA-specific features)
            if self.device == "cuda":
                logger.info("⚙️ Enabling CUDA optimizations...")
                if hasattr(self.pipeline, 'enable_attention_slicing'):
                    self.pipeline.enable_attention_slicing(1)
                    logger.info("  ✓ Attention slicing enabled")

                if hasattr(self.pipeline, 'enable_vae_slicing'):
                    self.pipeline.enable_vae_slicing()
                    logger.info("  ✓ VAE slicing enabled")

            self.model_loaded = True
            logger.info("✅ Model loaded successfully!")

            # Log GPU memory usage
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated(0) / 1e9
                memory_reserved = torch.cuda.memory_reserved(0) / 1e9
                logger.info(f"GPU Memory Allocated: {memory_allocated:.2f} GB")
                logger.info(f"GPU Memory Reserved: {memory_reserved:.2f} GB")

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    async def warmup(self, warmup_prompt: str = "test", size: int = 256, steps: int = 4) -> None:
        """
        Perform warmup inference to initialize CUDA kernels.

        Args:
            warmup_prompt: Simple prompt for warmup
            size: Small image size for quick warmup
            steps: Minimal inference steps
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        logger.info("🔥 Starting GPU warmup...")

        try:
            # Run a quick inference to warm up GPU (in thread pool)
            loop = asyncio.get_event_loop()
            _ = await loop.run_in_executor(
                self.executor,
                lambda: self.pipeline(
                    prompt=warmup_prompt,
                    height=size,
                    width=size,
                    num_inference_steps=steps,
                    guidance_scale=3.5
                ).images[0]
            )

            logger.info("✅ GPU warmup complete!")

        except Exception as e:
            logger.warning(f"Warmup failed (non-critical): {str(e)}")
    
    def _generate_image_sync(
        self,
        prompt: str,
        height: int,
        width: int,
        num_inference_steps: int,
        guidance_scale: float,
        generator: Optional[torch.Generator]
    ) -> Image.Image:
        """
        Synchronous image generation to run in thread pool.

        Args:
            prompt: Text prompt for image generation
            height: Output image height
            width: Output image width
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for generation
            generator: Random generator for reproducibility

        Returns:
            PIL Image object
        """
        result = self.pipeline(
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        )
        return result.images[0]

    async def generate_image(
        self,
        prompt: str,
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 28,
        guidance_scale: float = 3.5,
        seed: Optional[int] = None
    ) -> Image.Image:
        """
        Generate image using Flux model with concurrency control.

        Args:
            prompt: Text prompt for image generation
            height: Output image height
            width: Output image width
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for generation
            seed: Random seed for reproducibility

        Returns:
            PIL Image object

        Raises:
            RuntimeError: If model is not loaded
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Acquire semaphore for concurrency control
        async with self.semaphore:
            logger.info(f"Generating image: {prompt[:50]}...")

            try:
                # Set seed if provided
                generator = None
                if seed is not None:
                    generator = torch.Generator(device=self.device).manual_seed(seed)

                # Run inference in thread pool to avoid blocking event loop
                loop = asyncio.get_event_loop()
                image = await loop.run_in_executor(
                    self.executor,
                    self._generate_image_sync,
                    prompt,
                    height,
                    width,
                    num_inference_steps,
                    guidance_scale,
                    generator
                )

                logger.info(f"✅ Image generated: {width}x{height}")

                return image

            except Exception as e:
                logger.error(f"Image generation failed: {str(e)}")
                raise
    
    def cleanup(self) -> None:
        """Clean up GPU memory and thread pool"""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            self.model_loaded = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("GPU memory cleared")

        # Shutdown thread pool executor
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
            logger.info("Thread pool executor shutdown")
    
    def get_gpu_stats(self) -> dict:
        """Get current GPU statistics"""
        if torch.cuda.is_available():
            return {
                "gpu_available": True,
                "device_type": "cuda",
                "device_name": torch.cuda.get_device_name(0),
                "memory_allocated_gb": torch.cuda.memory_allocated(0) / 1e9,
                "memory_reserved_gb": torch.cuda.memory_reserved(0) / 1e9,
                "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
            }
        elif torch.backends.mps.is_available():
            return {
                "gpu_available": True,
                "device_type": "mps",
                "device_name": "Apple Silicon GPU (MPS)",
                "memory_info": "Shared with system RAM"
            }
        else:
            return {
                "gpu_available": False,
                "device_type": "cpu"
            }

