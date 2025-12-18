"""
Ollama Extractor Module
OCR extraction using Ollama-based vision models.
Supports: DeepSeek OCR, LLaVA, Llama-Vision, Qwen-VL, etc.
"""

from pathlib import Path
from typing import Optional
import time

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from ..config import OCRConfig
from ..parsers import parse_ocr_output
from ..utils import configure_proxy_bypass, check_ollama_running, verify_model_exists
from .base_extractor import BaseExtractor, ExtractionResult
from ..config import create_default_config

class OllamaExtractor(BaseExtractor):
    """
    OCR extractor using Ollama-based vision models.
    
    Supports any Ollama vision model including:
    - DeepSeek OCR (deepseek-ocr:3b, deepseek-ocr:7b)
    - LLaVA (llava:7b, llava:13b)
    - Llama-Vision (llama-vision:7b)
    - Qwen-VL (qwen-vl:7b)
    - Any other Ollama vision model
    """
    
    def __init__(self, config: Optional[OCRConfig] = None):
        """
        Initialize Ollama extractor.
        
        Args:
            config: OCR configuration (None = use defaults)
            
        Raises:
            RuntimeError: If Ollama library not available
            ConnectionError: If cannot connect to Ollama
            
        Example:
            >>> from config import OCRConfig
            >>> config = OCRConfig(model_name="deepseek-ocr:3b")
            >>> extractor = OllamaExtractor(config)
        """
        super().__init__(extractor_name="ollama_extractor")
        
        if not OLLAMA_AVAILABLE:
            raise RuntimeError(
                "Ollama library not available. Install with:\n"
                "  pip install ollama"
            )
        
        # Use provided config or create default
        # from config import create_default_config
        self.config = config or create_default_config()
        
        # Configure proxy bypass (important for corporate networks)
        configure_proxy_bypass()
        
        # Create Ollama client
        self.client = ollama.Client(host=self.config.host)
        
        # Verify connection and configuration
        if not self.validate_config():
            raise ConnectionError(
                f"Failed to validate Ollama configuration. "
                f"Please check connection to {self.config.host}"
            )
    
    def validate_config(self) -> bool:
        """
        Validate extractor configuration.
        
        Checks:
        - Ollama is running
        - Model is available (optional warning)
        
        Returns:
            bool: True if configuration is valid
        """
        # Check Ollama is running
        if not check_ollama_running(self.config.host):
            print(f"Warning: Cannot connect to Ollama at {self.config.host}")
            return False
        
        # Check if model exists (warning only, not fatal)
        if not verify_model_exists(self.config.model_name, self.config.host):
            print(f"Warning: Model '{self.config.model_name}' not found in Ollama.")
            print(f"Available models: run 'ollama list'")
            print(f"Pull model with: ollama pull {self.config.model_name}")
            # Don't fail - model might be pulled later
        
        return True
    
    def is_available(self) -> bool:
        """
        Check if extractor is available and ready.
        
        Returns:
            bool: True if Ollama is accessible
        """
        return check_ollama_running(self.config.host)
    
    def extract(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract text and structure from image using Ollama.
        
        Args:
            image_path: Path to image file
            custom_prompt: Override default prompt
            
        Returns:
            ExtractionResult: Extraction result with parsed elements
            
        Example:
            >>> extractor = OllamaExtractor()
            >>> result = extractor.extract("document.png")
            >>> print(f"Found {result.get_element_count()} elements")
            >>> for elem in result.get_elements():
            ...     print(f"{elem.element_type}: {elem.bbox}")
        """
        image_path = Path(image_path)
        
        # Validate image exists
        if not self.validate_image_path(str(image_path)):
            return self.create_error_result(
                image_path=str(image_path),
                error_message=f"Invalid or missing image: {image_path}",
                model_name=self.config.model_name
            )
        
        # Get prompt
        prompt = custom_prompt or self.config.get_prompt()
        
        # Get model parameters
        model_params = self.config.get_merged_model_params()
        
        try:
            start_time = time.time()
            
            # Call Ollama API
            response = self.client.generate(
                model=self.config.model_name,
                prompt=prompt,
                images=[str(image_path)],
                options=model_params,
                stream=False
            )
            
            processing_time = time.time() - start_time
            
            # Extract raw output
            raw_output = response.get('response', '')
            
            if not raw_output:
                return self.create_error_result(
                    image_path=str(image_path),
                    error_message="Empty response from model",
                    model_name=self.config.model_name
                )
            
            # Parse output
            parse_result = parse_ocr_output(raw_output)
            
            # # ========== NEW: Auto-scale bounding boxes (as of now not requires )==========
            # from PIL import Image
            
            # # Get original image size
            # img = Image.open(image_path)
            # original_width, original_height = img.size
            
            # # Scale bboxes if needed
            # if parse_result and parse_result.elements:
            #     # Find max coordinates
            #     max_x = 0
            #     max_y = 0
            #     for elem in parse_result.elements:
            #         if elem.bbox:
            #             max_x = max(max_x, elem.bbox[2])
            #             max_y = max(max_y, elem.bbox[3])
                
            #     # If max coords are much smaller than image, scale is needed
            #     if max_x > 0 and max_y > 0 and (max_x < original_width * 0.7 or max_y < original_height * 0.7):
            #         # Calculate scale factors
            #         scale_x = original_width / max_x
            #         scale_y = original_height / max_y
            #         scale = min(scale_x, scale_y)  # Use minimum to avoid overflow
                    
            #         print(f"    [BBOX AUTO-SCALING]")
            #         print(f"      Image size: {original_width} × {original_height}")
            #         print(f"      Model coords: ~{max_x} × ~{max_y}")
            #         print(f"      Scale factor: {scale:.2f}x")
                    
            #         # Scale all bounding boxes
            #         for elem in parse_result.elements:
            #             if elem.bbox:
            #                 elem.bbox = [
            #                     int(elem.bbox[0] * scale),
            #                     int(elem.bbox[1] * scale),
            #                     int(elem.bbox[2] * scale),
            #                     int(elem.bbox[3] * scale)
            #                 ]
                    
            #         print(f"      ✓ Scaled {len(parse_result.elements)} bboxes")
            # # ===================================================

            # Calculate processing time
            processing_time = time.time() - start_time
            # Create result
            return ExtractionResult(
                raw_output=raw_output,
                parse_result=parse_result,
                model_name=self.config.model_name,
                prompt_used=prompt,
                image_path=str(image_path),
                processing_time=processing_time,
                success=True,
                metadata={
                    'ollama_host': self.config.host,
                    'model_params': model_params
                }
            )
        
        except Exception as e:
            return self.create_error_result(
                image_path=str(image_path),
                error_message=f"Extraction failed: {str(e)}",
                model_name=self.config.model_name
            )
    
    def get_info(self) -> dict:
        """
        Get information about this extractor.
        
        Returns:
            dict: Extractor information including model details
            
        Example:
            >>> extractor = OllamaExtractor()
            >>> info = extractor.get_info()
            >>> print(info['model_name'])
            'deepseek-ocr:3b'
        """
        base_info = super().get_info()
        
        ollama_info = {
            'model_name': self.config.model_name,
            'host': self.config.host,
            'use_grounding': self.config.use_grounding,
            'supports_grounding': self.config.supports_grounding(),
            'parameters': self.config.get_merged_model_params(),
            'prompt_key': self.config.prompt_key
        }
        
        base_info.update(ollama_info)
        return base_info


if __name__ == "__main__":
    print("Testing ollama_extractor.py...\n")
    
    if not OLLAMA_AVAILABLE:
        print("❌ Ollama library not available!")
        print("Install with: pip install ollama")
        exit(1)
    
    print("✅ Ollama library available")
    
    # Test 1: Create extractor with default config
    print("\nTest 1: Create Extractor (Default Config)")
    print("-" * 60)
    
    try:
        from config import create_default_config
        config = create_default_config()
        extractor = OllamaExtractor(config)
        print(f"✓ Extractor created")
        print(f"  Model: {extractor.config.model_name}")
        print(f"  Host: {extractor.config.host}")
        print(f"  Extractor name: {extractor.get_extractor_name()}")
    except Exception as e:
        print(f"✗ Could not create extractor: {e}")
        print("\nMake sure:")
        print("  1. Ollama is running: ollama serve")
        print("  2. Model is available: ollama list")
        exit(1)
    
    # Test 2: Check availability
    print("\n" + "="*60)
    print("Test 2: Check Availability")
    print("-" * 60)
    is_available = extractor.is_available()
    print(f"Extractor available: {is_available}")
    
    # Test 3: Get extractor info
    print("\n" + "="*60)
    print("Test 3: Get Extractor Info")
    print("-" * 60)
    info = extractor.get_info()
    print(f"Model: {info['model_name']}")
    print(f"Supports grounding: {info['supports_grounding']}")
    print(f"Host: {info['host']}")
    print(f"Parameters:")
    for key, value in info['parameters'].items():
        print(f"  {key}: {value}")
    
    # Test 4: Test with invalid image (should fail gracefully)
    print("\n" + "="*60)
    print("Test 4: Invalid Image Path")
    print("-" * 60)
    result = extractor.extract("nonexistent.png")
    print(f"Success: {result.success}")
    print(f"Error: {result.error_message}")
    
    # Test 5: Validate image path
    print("\n" + "="*60)
    print("Test 5: Validate Image Path")
    print("-" * 60)
    is_valid = extractor.validate_image_path("test.png")
    print(f"'test.png' valid: {is_valid}")
    is_valid = extractor.validate_image_path("test.txt")
    print(f"'test.txt' valid: {is_valid}")
    
    # Test 6: Create test image and extract (if possible)
    print("\n" + "="*60)
    print("Test 6: Extract from Test Image")
    print("-" * 60)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        
        # Create test image with text
        temp_dir = Path(tempfile.mkdtemp())
        test_image = temp_dir / "test.png"
        
        img = Image.new('RGB', (800, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some text
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 80), "Test Document - OCR", fill='black', font=font)
        img.save(test_image)
        
        print(f"Created test image: {test_image}")
        
        # Extract (this will actually call Ollama)
        print("Calling Ollama for extraction...")
        result = extractor.extract(str(test_image))
        
        print(f"\nExtraction Result:")
        print(f"  Success: {result.success}")
        print(f"  Processing time: {result.processing_time:.2f}s")
        print(f"  Elements found: {result.get_element_count()}")
        print(f"  Parser used: {result.parse_result.parser_type}")
        
        if result.success:
            print(f"\nFirst 200 chars of raw output:")
            print(result.raw_output[:200])
            
            if result.get_element_count() > 0:
                print(f"\nFirst element:")
                elem = result.get_elements()[0]
                print(f"  Type: {elem.element_type}")
                print(f"  BBox: {elem.bbox}")
                content_preview = elem.content[:100] + "..." if len(elem.content) > 100 else elem.content
                print(f"  Content: {content_preview}")
        else:
            print(f"\nExtraction failed: {result.error_message}")
        
        # Test 7: Test to_dict()
        print("\n" + "="*60)
        print("Test 7: Result to Dict")
        print("-" * 60)
        result_dict = result.to_dict()
        print(f"Dict keys: {list(result_dict.keys())}")
        print(f"Success: {result_dict['success']}")
        print(f"Element count: {result_dict['element_count']}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"Could not test extraction: {e}")
        print("This is expected if Ollama is not running or model not available")
    
    print("\n✅ ollama_extractor.py tests completed!")