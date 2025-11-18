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
        self.device: str = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded: bool = False
        self.semaphore: Optional[asyncio.Semaphore] = None
        
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
    
    async def load_model(self, model_name: str, use_fp16: bool = True) -> None:
        """
        Load Flux model into GPU memory.
        
        Args:
            model_name: HuggingFace model name or local path
            use_fp16: Use FP16 precision for faster inference
            
        Raises:
            RuntimeError: If CUDA is not available or model loading fails
        """
        if self.model_loaded:
            logger.info("Model already loaded, skipping...")
            return
            
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available. This backend requires GPU support.")
        
        logger.info(f"Loading Flux model: {model_name}")
        logger.info(f"Device: {self.device}")
        logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        logger.info(f"Available GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        
        try:
            # Load pipeline with optimizations
            dtype = torch.float16 if use_fp16 else torch.float32
            
            self.pipeline = FluxPipeline.from_pretrained(
                model_name,
                torch_dtype=dtype,
                use_safetensors=True
            )
            
            # Move to GPU
            self.pipeline = self.pipeline.to(self.device)
            
            # Enable memory optimizations
            if hasattr(self.pipeline, 'enable_model_cpu_offload'):
                # For very large models, enable CPU offloading
                # self.pipeline.enable_model_cpu_offload()
                pass
            
            if hasattr(self.pipeline, 'enable_attention_slicing'):
                self.pipeline.enable_attention_slicing(1)
            
            if hasattr(self.pipeline, 'enable_vae_slicing'):
                self.pipeline.enable_vae_slicing()
            
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
            # Run a quick inference to warm up GPU
            _ = self.pipeline(
                prompt=warmup_prompt,
                height=size,
                width=size,
                num_inference_steps=steps,
                guidance_scale=3.5
            ).images[0]
            
            logger.info("✅ GPU warmup complete!")
            
        except Exception as e:
            logger.warning(f"Warmup failed (non-critical): {str(e)}")
    
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
                
                # Run inference
                result = self.pipeline(
                    prompt=prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator
                )
                
                image = result.images[0]
                logger.info(f"✅ Image generated: {width}x{height}")
                
                return image
                
            except Exception as e:
                logger.error(f"Image generation failed: {str(e)}")
                raise
    
    def cleanup(self) -> None:
        """Clean up GPU memory"""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            self.model_loaded = False
            
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("GPU memory cleared")
    
    def get_gpu_stats(self) -> dict:
        """Get current GPU statistics"""
        if not torch.cuda.is_available():
            return {"gpu_available": False}
        
        return {
            "gpu_available": True,
            "device_name": torch.cuda.get_device_name(0),
            "memory_allocated_gb": torch.cuda.memory_allocated(0) / 1e9,
            "memory_reserved_gb": torch.cuda.memory_reserved(0) / 1e9,
            "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
        }

