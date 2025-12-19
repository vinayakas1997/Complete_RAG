"""
HuggingFace DeepSeek OCR Extractor
Direct integration with transformers for maximum speed and control.
"""

from pathlib import Path
from typing import Optional
import time
import os

try:
    from transformers import AutoModel, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from ..config import OCRConfig
from ..parsers import parse_ocr_output
from .base_extractor import BaseExtractor, ExtractionResult


class HuggingFaceExtractor(BaseExtractor):
    """
    DeepSeek OCR extractor using HuggingFace transformers.
    
    Provides direct model access with full control:
    - 5-10x faster than Ollama
    - No HTTP overhead
    - Full parameter control
    - Better debugging
    
    Example:
        >>> extractor = HuggingFaceExtractor(
        ...     model_name="deepseek-ai/DeepSeek-OCR",
        ...     device="cuda:0",
        ...     image_size=1024
        ... )
        >>> result = extractor.extract("document.png")
    """
    
    def __init__(
        self,
        config: Optional[OCRConfig] = None,
        model_name: str = "deepseek-ai/DeepSeek-OCR",
        device: str = "cuda:0",
        image_size: int = 1024,
        base_size: int = 1024,
        crop_mode: bool = True,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize HuggingFace extractor.
        
        Args:
            config: OCR configuration (optional)
            model_name: HuggingFace model ID
            device: Device to use ('cuda:0', 'cuda:1', 'cpu')
            image_size: Target image resolution (640, 1024, 1280)
            base_size: Base resolution for processing
            crop_mode: Enable cropping mode
            cache_dir: Custom cache directory (e.g., "D:/huggingface_models")
        
        Example:
            >>> # Use custom cache directory on D: drive
            >>> extractor = HuggingFaceExtractor(
            ...     cache_dir="D:/AI_Models/huggingface"
            ... )
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers and torch are required for HuggingFaceExtractor.\n"
                "Install with: pip install transformers torch"
            )
        
        self.config = config or OCRConfig(model_name=model_name)
        self.model_name = model_name
        self.device = device
        self.image_size = image_size
        self.base_size = base_size
        self.crop_mode = crop_mode
        self.cache_dir = cache_dir
        
        # Set cache directory if provided
        if cache_dir:
            os.environ['TRANSFORMERS_CACHE'] = cache_dir
            os.environ['HF_HOME'] = cache_dir
            print(f"Using custom cache directory: {cache_dir}")
        
        # Check CUDA availability
        if device.startswith('cuda'):
            if not torch.cuda.is_available():
                print("⚠️  CUDA not available! Falling back to CPU")
                self.device = 'cpu'
            else:
                # Verify GPU index
                gpu_index = int(device.split(':')[1]) if ':' in device else 0
                if gpu_index >= torch.cuda.device_count():
                    print(f"⚠️  GPU {gpu_index} not found! Using GPU 0")
                    self.device = 'cuda:0'
                else:
                    print(f"✓ Using GPU {gpu_index}: {torch.cuda.get_device_name(gpu_index)}")
        
        # Load model
        print(f"\n{'='*60}")
        print("Loading DeepSeek OCR from HuggingFace...")
        print(f"{'='*60}")
        print(f"  Model: {model_name}")
        print(f"  Device: {self.device}")
        print(f"  Image size: {image_size}×{image_size}")
        print(f"  Cache dir: {cache_dir or 'default (~/.cache/huggingface)'}")
        
        load_start = time.time()
        
        try:
            # Load tokenizer
            print("\n[1/2] Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir=cache_dir
            )
            print("      ✓ Tokenizer loaded")
            
            # Load model
            print("\n[2/2] Loading model...")
            
            # Determine dtype based on device
            if self.device == 'cpu':
                dtype = torch.float32
                print("      Using dtype: float32 (CPU)")
            else:
                dtype = torch.bfloat16
                print("      Using dtype: bfloat16 (GPU)")
            
            self.model = AutoModel.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=dtype,
                cache_dir=cache_dir
            )
            
            # Move to device
            if self.device.startswith('cuda'):
                self.model = self.model.cuda(self.device)
            
            # Set to eval mode
            self.model = self.model.eval()
            
            load_time = time.time() - load_start
            print(f"      ✓ Model loaded in {load_time:.2f}s")
            
            # Show memory usage
            if self.device.startswith('cuda'):
                gpu_index = int(self.device.split(':')[1]) if ':' in self.device else 0
                memory_allocated = torch.cuda.memory_allocated(gpu_index) / 1024**3
                memory_reserved = torch.cuda.memory_reserved(gpu_index) / 1024**3
                print(f"\n      GPU Memory:")
                print(f"        Allocated: {memory_allocated:.2f} GB")
                print(f"        Reserved: {memory_reserved:.2f} GB")
            
            print(f"\n{'='*60}")
            print("✓ HuggingFace extractor ready!")
            print(f"{'='*60}\n")
        
        except Exception as e:
            print(f"\n✗ Failed to load model: {e}")
            raise
    
    def validate_config(self) -> bool:
        """Validate configuration."""
        return self.model is not None and self.tokenizer is not None
    
    def is_available(self) -> bool:
        """Check if extractor is ready."""
        return self.model is not None
    
    def extract(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract text and elements from image.
        
        Args:
            image_path: Path to image file
            custom_prompt: Override default prompt
            
        Returns:
            ExtractionResult: Extraction results
        """
        start_time = time.time()
        
        # Validate image
        if not self.validate_image_path(image_path):
            return self.create_error_result(
                image_path=image_path,
                error_message=f"Invalid image path: {image_path}"
            )
        
        try:
            # Get prompt
            if custom_prompt is None:
                if self.config and self.config.use_grounding:
                    custom_prompt = "<image>\n<|grounding|>Convert the document to markdown."
                else:
                    custom_prompt = "<image>\nFree OCR."
            
            # Run inference
            print(f"    [HF] Running inference on {Path(image_path).name}...")
            inference_start = time.time()
            
            with torch.no_grad():
                result_dict = self.model.infer(
                    self.tokenizer,
                    prompt=custom_prompt,
                    image_file=image_path,
                    base_size=self.base_size,
                    image_size=self.image_size,
                    crop_mode=self.crop_mode,
                    save_results=False,  # We handle saving ourselves
                    test_compress=False
                )
            
            inference_time = time.time() - inference_start
            print(f"    [HF] Inference completed in {inference_time:.2f}s")
            
            # Extract response
            if isinstance(result_dict, dict):
                raw_output = result_dict.get('response', '')
            else:
                raw_output = str(result_dict)
            
            if not raw_output:
                return self.create_error_result(
                    image_path=image_path,
                    error_message="Empty response from model"
                )
            
            # Parse output
            parse_result = parse_ocr_output(raw_output)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            print(f"    [HF] Total time: {processing_time:.2f}s")
            print(f"    [HF] Extracted {parse_result.element_count} elements")
            
            # Create result
            return ExtractionResult(
                raw_output=raw_output,
                parse_result=parse_result,
                model_name=self.model_name,
                prompt_used=custom_prompt,
                image_path=image_path,
                processing_time=processing_time,
                success=True
            )
        
        except Exception as e:
            print(f"    [HF] ✗ Error: {str(e)}")
            return self.create_error_result(
                image_path=image_path,
                error_message=f"Extraction failed: {str(e)}"
            )
    
    def extract_with_retry(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract with retry logic.
        
        Args:
            image_path: Path to image file
            custom_prompt: Override default prompt
            
        Returns:
            ExtractionResult: Extraction results
        """
        max_retries = getattr(self.config, 'max_retries', 2) if self.config else 2
        retry_delay = getattr(self.config, 'retry_delay', 2) if self.config else 2
        
        for attempt in range(max_retries):
            try:
                return self.extract(image_path, custom_prompt)
            
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Retry {attempt + 1}/{max_retries - 1}: {str(e)}")
                    time.sleep(retry_delay)
                else:
                    # Last attempt failed
                    return self.create_error_result(
                        image_path=image_path,
                        error_message=f"All retries failed: {str(e)}"
                    )
    
    def get_info(self) -> dict:
        """Get extractor information."""
        return {
            'extractor_type': 'huggingface',
            'model_name': self.model_name,
            'device': self.device,
            'image_size': f"{self.image_size}×{self.image_size}",
            'base_size': self.base_size,
            'crop_mode': self.crop_mode,
            'supports_grounding': True,
            'backend': 'HuggingFace Transformers'
        }
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            if hasattr(self, 'model') and self.model is not None:
                # Clear GPU memory
                if self.device.startswith('cuda'):
                    del self.model
                    torch.cuda.empty_cache()
        except:
            pass


if __name__ == "__main__":
    print("Testing HuggingFaceExtractor...")
    
    # Test 1: Check dependencies
    print("\nTest 1: Dependencies")
    print("-" * 60)
    print(f"Transformers available: {TRANSFORMERS_AVAILABLE}")
    if TRANSFORMERS_AVAILABLE:
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    
    print("\n✓ HuggingFaceExtractor module loaded successfully!")