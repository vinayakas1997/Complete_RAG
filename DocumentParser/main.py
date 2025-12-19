"""
Main OCR System Module
Top-level interface for document OCR processing.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from .config import (
    OCRConfig,
    create_default_config,
    create_fast_config,
    create_quality_config,
    print_config_summary
)
from .extractors import OllamaExtractor, MultiPageProcessor, DocumentResult
from .processors import PDFProcessor, ImageProcessor
from .utils import is_pdf, is_supported_image


"""
HuggingFaceOCR - Main Class
High-performance OCR using HuggingFace transformers.
"""

# from pathlib import Path
# from typing import Optional, List

from .config import OCRConfig, OutputConfig, get_full_output_config
from .extractors import HuggingFaceExtractor, MultiPageProcessor

class OllamaOCR:
    """
    Complete OCR system for Ollama-based vision models.
    
    Supports:
    - DeepSeek OCR (deepseek-ocr:3b, deepseek-ocr:7b)
    - LLaVA (llava:7b, llava:13b, llava:34b)
    - Llama-Vision (llama-vision:7b)
    - Qwen-VL (qwen-vl:7b)
    - Any other Ollama vision model
    
    Features:
    - Multi-page PDF processing
    - Grounding detection (bounding boxes)
    - Multiple output formats (raw, JSON, markdown)
    - Automatic visualization
    - Configurable output organization
    
    Example:
        >>> from main import OllamaOCR
        >>> 
        >>> # Simple usage
        >>> ocr = OllamaOCR()
        >>> result = ocr.process("document.pdf")
        >>> print(f"Processed {result.page_count} pages")
        >>> 
        >>> # Custom configuration
        >>> ocr = OllamaOCR(
        ...     model_name="llava:13b",
        ...     use_grounding=True,
        ...     output_dir="my_output"
        ... )
        >>> result = ocr.process("manual.pdf", page_range=(1, 10))
    """
    
    def __init__(
        self,
        model_name: str = "deepseek-ocr:3b",
        config: Optional[OCRConfig] = None,
        use_grounding: bool = True,
        output_dir: Optional[str] = None,
        save_annotations: bool = True,
        quality_mode: bool = False
    ):
        """
        Initialize OllamaOCR system.
        
        Args:
            model_name: Ollama model to use
            config: Custom OCR configuration (None = auto-create)
            use_grounding: Enable bounding box detection
            output_dir: Output directory (None = use default "output")
            save_annotations: Save annotated images with bounding boxes
            quality_mode: Use quality-optimized settings (slower but better)
            
        Example:
            >>> # Default settings
            >>> ocr = OllamaOCR()
            >>> 
            >>> # Custom model
            >>> ocr = OllamaOCR(model_name="llava:13b")
            >>> 
            >>> # Quality mode
            >>> ocr = OllamaOCR(quality_mode=True)
        """
        # Create or use provided config
        if config is None:
            if quality_mode:
                config = create_quality_config()
            else:
                config = create_default_config()
            
            # Apply parameters
            config.model_name = model_name
            config.use_grounding = use_grounding
            
            if output_dir:
                config.output_config.output_base_dir = output_dir
            
            if save_annotations is not None:
                config.save_annotation_copy = save_annotations
        
        self.config = config
        
        # Initialize components
        self.extractor = OllamaExtractor(self.config)
        self.processor = MultiPageProcessor(
            extractor=self.extractor,
            output_config=self.config.output_config
        )
        
        # Validate configuration
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate that the system is properly configured"""
        # Check if extractor is available
        if not self.extractor.is_available():
            raise ConnectionError(
                f"Cannot connect to Ollama. Please ensure:\n"
                f"1. Ollama is running: ollama serve\n"
                f"2. Model is available: ollama list\n"
                f"3. Host is correct: {self.config.host}"
            )
        
        # Validate configuration
        try:
            self.config.validate()
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")
    
    def process(
        self,
        file_path: str,
        page_range: Optional[tuple] = None,
        custom_prompt: Optional[str] = None,
        verbose: bool = True
    ) -> DocumentResult:
        """
        Process a document (PDF or image).
        
        Args:
            file_path: Path to document file
            page_range: Optional (start, end) page numbers for PDFs
            custom_prompt: Override default OCR prompt
            verbose: Print processing information
            
        Returns:
            DocumentResult: Complete processing result
            
        Example:
            >>> ocr = OllamaOCR()
            >>> 
            >>> # Process entire PDF
            >>> result = ocr.process("document.pdf")
            >>> 
            >>> # Process specific pages
            >>> result = ocr.process("document.pdf", page_range=(1, 5))
            >>> 
            >>> # Custom prompt
            >>> result = ocr.process(
            ...     "document.pdf",
            ...     custom_prompt="Extract all tables and text"
            ... )
        """
        file_path = Path(file_path)
        
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file type
        if not is_pdf(str(file_path)) and not is_supported_image(str(file_path)):
            raise ValueError(
                f"Unsupported file type: {file_path.suffix}\n"
                f"Supported: PDF, PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP"
            )
        
        if verbose:
            print("\n" + "="*60)
            print(f"Processing: {file_path.name}")
            print("="*60)
            print(f"Model: {self.config.model_name}")
            print(f"Use grounding: {self.config.use_grounding}")
            print(f"Output: {self.config.output_config.output_base_dir}")
            print("-"*60)
        
        # Process document
        result = self.processor.process_document(
            file_path=str(file_path),
            custom_prompt=custom_prompt,
            page_range=page_range
        )
        
        if verbose:
            self._print_summary(result)
        
        return result
    
    def _print_summary(self, result: DocumentResult):
        """Print processing summary"""
        print("\n" + "="*60)
        print("PROCESSING COMPLETE")
        print("="*60)
        print(f"Status: {'✓ Success' if result.success else '✗ Failed'}")
        print(f"Pages processed: {result.page_count}")
        print(f"Successful pages: {result.get_successful_pages()}")
        
        if result.get_failed_pages():
            print(f"Failed pages: {result.get_failed_pages()}")
        
        print(f"Total elements: {result.get_total_elements()}")
        print(f"Processing time: {result.total_processing_time:.2f}s")
        print(f"Output directory: {result.output_dir}")
        print("="*60 + "\n")
    
    def process_batch(
        self,
        file_paths: List[str],
        page_range: Optional[tuple] = None,
        custom_prompt: Optional[str] = None,
        verbose: bool = True
    ) -> List[DocumentResult]:
        """
        Process multiple documents in batch.
        
        Args:
            file_paths: List of document paths
            page_range: Optional page range for all documents
            custom_prompt: Optional custom prompt for all documents
            verbose: Print processing information
            
        Returns:
            List[DocumentResult]: Results for each document
            
        Example:
            >>> ocr = OllamaOCR()
            >>> files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
            >>> results = ocr.process_batch(files)
            >>> 
            >>> for result in results:
            ...     print(f"{result.input_file}: {result.page_count} pages")
        """
        results = []
        
        if verbose:
            print(f"\nProcessing {len(file_paths)} documents...")
        
        for i, file_path in enumerate(file_paths, 1):
            if verbose:
                print(f"\n[{i}/{len(file_paths)}] Processing: {Path(file_path).name}")
            
            try:
                result = self.process(
                    file_path=file_path,
                    page_range=page_range,
                    custom_prompt=custom_prompt,
                    verbose=False
                )
                results.append(result)
                
                if verbose:
                    print(f"  ✓ Success: {result.page_count} pages, {result.get_total_elements()} elements")
            
            except Exception as e:
                if verbose:
                    print(f"  ✗ Failed: {e}")
                # Add error result
                from extractors import DocumentResult
                error_result = DocumentResult(
                    input_file=file_path,
                    output_dir="",
                    page_count=0,
                    page_results=[],
                    total_processing_time=0.0,
                    success=False,
                    error_message=str(e)
                )
                results.append(error_result)
        
        if verbose:
            successful = sum(1 for r in results if r.success)
            print(f"\n✓ Batch complete: {successful}/{len(file_paths)} successful")
        
        return results
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            dict: System configuration and status
            
        Example:
            >>> ocr = OllamaOCR()
            >>> info = ocr.get_info()
            >>> print(f"Model: {info['model_name']}")
            >>> print(f"Available: {info['is_available']}")
        """
        return {
            'model_name': self.config.model_name,
            'host': self.config.host,
            'use_grounding': self.config.use_grounding,
            'supports_grounding': self.config.supports_grounding(),
            'is_available': self.extractor.is_available(),
            'output_dir': self.config.output_config.output_base_dir,
            'extractor_info': self.extractor.get_info()
        }
    
    def print_config(self):
        """
        Print current configuration.
        
        Example:
            >>> ocr = OllamaOCR()
            >>> ocr.print_config()
        """
        print_config_summary(self.config)


# Convenience function
def create_ocr(
    model_name: str = "deepseek-ocr:3b",
    **kwargs
) -> OllamaOCR:
    """
    Convenience function to create OCR system.
    
    Args:
        model_name: Model to use
        **kwargs: Additional arguments for OllamaOCR
        
    Returns:
        OllamaOCR: Configured OCR system
        
    Example:
        >>> ocr = create_ocr("llava:13b", output_dir="my_output")
        >>> result = ocr.process("document.pdf")
    """
    return OllamaOCR(model_name=model_name, **kwargs)





class HuggingFaceOCR:
    """
    OCR system using HuggingFace transformers (Direct model access).
    
    Advantages over OllamaOCR:
    - 5-10x faster (no HTTP overhead)
    - Full parameter control
    - Better debugging
    - Predictable performance
    - No external server required
    
    Example:
        >>> ocr = HuggingFaceOCR()
        >>> result = ocr.process("document.pdf")
        >>> print(f"Pages: {result.page_count}")
        
        >>> # Use custom cache directory on D: drive
        >>> ocr = HuggingFaceOCR(cache_dir="D:/AI_Models/huggingface")
        
        >>> # Use specific GPU
        >>> ocr = HuggingFaceOCR(device="cuda:1")
        
        >>> # Batch processing
        >>> results = ocr.process_batch(["doc1.pdf", "doc2.pdf"])
    """
    
    def __init__(
        self,
        model_name: str = "deepseek-ai/DeepSeek-OCR",
        config: Optional[OCRConfig] = None,
        device: str = "cuda:0",
        image_size: int = 1024,
        output_dir: Optional[str] = None,
        save_annotations: bool = True,
        quality_mode: bool = False,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize HuggingFaceOCR.
        
        Args:
            model_name: HuggingFace model ID
            config: OCR configuration (auto-created if None)
            device: Device to use ('cuda:0', 'cuda:1', 'cpu')
            image_size: Target resolution (640, 1024, 1280)
            output_dir: Output directory
            save_annotations: Enable annotated images
            quality_mode: Use higher quality settings (slower)
            cache_dir: Custom model cache directory (e.g., "D:/AI_Models")
        
        Example:
            >>> # Basic usage
            >>> ocr = HuggingFaceOCR()
            
            >>> # Custom cache on D: drive
            >>> ocr = HuggingFaceOCR(
            ...     cache_dir="D:/AI_Models/huggingface",
            ...     device="cuda:0",
            ...     output_dir="my_output"
            ... )
            
            >>> # Quality mode (slower but better)
            >>> ocr = HuggingFaceOCR(
            ...     quality_mode=True,
            ...     image_size=1280  # Higher resolution
            ... )
        """
        
        # Create config if not provided
        if config is None:
            # Get appropriate output config
            if save_annotations:
                output_config = get_full_output_config()
            else:
                output_config = OutputConfig()
            
            # Apply output directory
            if output_dir:
                output_config.output_base_dir = output_dir
            
            # Create OCR config
            config = OCRConfig(
                model_name=model_name,
                output_config=output_config,
                use_grounding=True,
                # temperature=0.0,
                # context_length=8192
            )
            
            # Quality mode settings
            if quality_mode:
                config.context_length = 16384
                image_size = max(image_size, 1280)
        
        # Apply output_dir override
        if output_dir:
            config.output_config.output_base_dir = output_dir
        
        # Store config
        self.config = config
        self.device = device
        self.image_size = image_size
        self.cache_dir = cache_dir
        
        # Create HuggingFace extractor
        print("\n" + "="*80)
        print("Initializing HuggingFaceOCR")
        print("="*80)
        
        self.extractor = HuggingFaceExtractor(
            config=config,
            model_name=model_name,
            device=device,
            image_size=image_size,
            cache_dir=cache_dir
        )
        
        # Create multi-page processor
        self.processor = MultiPageProcessor(
            extractor=self.extractor,
            output_config=config.output_config
        )
        
        print("✓ HuggingFaceOCR initialized")
        print(f"  Device: {device}")
        print(f"  Image size: {image_size}×{image_size}")
        print(f"  Output: {config.output_config.output_base_dir}")
        print(f"  Cache: {cache_dir or 'default'}")
        print("="*80 + "\n")
    
    def process(
        self,
        file_path: str,
        custom_prompt: Optional[str] = None,
        page_range: Optional[tuple] = None,
        verbose: bool = False
    ):
        """
        Process a document (PDF or image).
        
        Args:
            file_path: Path to document
            custom_prompt: Override default prompt
            page_range: Tuple (start, end) for page selection
            verbose: Show detailed progress
            
        Returns:
            DocumentResult: Processing results
            
        Example:
            >>> ocr = HuggingFaceOCR()
            >>> result = ocr.process("document.pdf")
            >>> print(f"Pages: {result.page_count}")
            >>> print(f"Elements: {result.get_total_elements()}")
            
            >>> # Process specific pages
            >>> result = ocr.process("large.pdf", page_range=(1, 5))
            
            >>> # Custom prompt
            >>> result = ocr.process(
            ...     "tables.pdf",
            ...     custom_prompt="<image>\\n<|grounding|>Extract only tables."
            ... )
        """
        return self.processor.process_document(
            file_path=file_path,
            custom_prompt=custom_prompt,
            page_range=page_range,
            verbose=verbose
        )
    
    def process_batch(
        self,
        file_paths: List[str],
        custom_prompt: Optional[str] = None,
        verbose: bool = False
    ) -> List:
        """
        Process multiple documents.
        
        Args:
            file_paths: List of document paths
            custom_prompt: Override default prompt
            verbose: Show detailed progress
            
        Returns:
            List of DocumentResult objects
            
        Example:
            >>> ocr = HuggingFaceOCR()
            >>> files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
            >>> results = ocr.process_batch(files)
            >>> 
            >>> for result in results:
            ...     if result.success:
            ...         print(f"✓ {result.input_file}: {result.page_count} pages")
        """
        results = []
        
        for idx, file_path in enumerate(file_paths, 1):
            print(f"\n[{idx}/{len(file_paths)}] Processing: {Path(file_path).name}")
            print("-" * 80)
            
            try:
                result = self.process(
                    file_path=file_path,
                    custom_prompt=custom_prompt,
                    verbose=verbose
                )
                results.append(result)
            
            except Exception as e:
                print(f"✗ Error: {e}")
                # Create error result
                from .extractors.multipage_processor import DocumentResult
                error_result = DocumentResult(
                    input_file=file_path,
                    success=False,
                    error_message=str(e),
                    page_results=[],
                    output_dir="",
                    total_processing_time=0.0
                )
                results.append(error_result)
        
        return results
    
    def get_info(self) -> dict:
        """
        Get OCR system information.
        
        Returns:
            dict: System information
            
        Example:
            >>> ocr = HuggingFaceOCR()
            >>> info = ocr.get_info()
            >>> print(f"Device: {info['device']}")
            >>> print(f"Model: {info['model']}")
        """
        return {
            'ocr_type': 'HuggingFaceOCR',
            'model': self.config.model_name,
            'device': self.device,
            'image_size': self.image_size,
            'cache_dir': self.cache_dir,
            'output_dir': self.config.output_config.output_base_dir,
            'extractor_info': self.extractor.get_info()
        }
    
    def __repr__(self):
        """String representation."""
        return (
            f"HuggingFaceOCR("
            f"model='{self.config.model_name}', "
            f"device='{self.device}', "
            f"image_size={self.image_size})"
        )


def create_huggingface_ocr(
    device: str = "cuda:0",
    output_dir: str = "output",
    cache_dir: Optional[str] = None,
    **kwargs
) -> HuggingFaceOCR:
    """
    Factory function to create HuggingFaceOCR instance.
    
    Args:
        device: Device to use
        output_dir: Output directory
        cache_dir: Custom cache directory
        **kwargs: Additional arguments for HuggingFaceOCR
        
    Returns:
        HuggingFaceOCR instance
        
    Example:
        >>> ocr = create_huggingface_ocr(
        ...     device="cuda:0",
        ...     cache_dir="D:/AI_Models"
        ... )
    """
    return HuggingFaceOCR(
        device=device,
        output_dir=output_dir,
        cache_dir=cache_dir,
        **kwargs
    )


# if __name__ == "__main__":
#     print("Testing HuggingFaceOCR...")
    
#     # Create instance
#     ocr = HuggingFaceOCR(
#         device="cuda:0",
#         cache_dir=None  # Use default
#     )
    
#     # Show info
#     info = ocr.get_info()
#     print("\nOCR Info:")
#     for key, value in info.items():
#         print(f"  {key}: {value}")
    
#     print("\n✓ HuggingFaceOCR ready to use!")


if __name__ == "__main__":
    print("Testing main.py...\n")
    
    print("Available functions:")
    print("  - OllamaOCR: Main OCR class")
    print("  - create_ocr: Convenience function")
    
    print("\nUsage examples:")
    print("""
    # Simple usage
    from main import OllamaOCR
    
    ocr = OllamaOCR()
    result = ocr.process("document.pdf")
    print(f"Processed {result.page_count} pages")
    
    # Custom model
    ocr = OllamaOCR(model_name="llava:13b")
    result = ocr.process("manual.pdf")
    
    # Batch processing
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    results = ocr.process_batch(files)
    
    # Quality mode
    ocr = OllamaOCR(quality_mode=True)
    result = ocr.process("important_doc.pdf")
    """)
    
    print("\n✅ main.py ready!")
# ```

# ---

# ## 🎉 **PROJECT COMPLETE!** 🎉

# You now have a **complete, production-grade OCR system!**

# ---

# ## Final Project Structure:
# ```
# deepseek_ocr_project/
# ├── main.py                    ✅ Main entry point
# ├── requirements.txt           ✅ Dependencies
# ├── utils/                     ✅ File & network utilities
# │   ├── __init__.py
# │   ├── file_utils.py
# │   └── network_utils.py
# ├── config/                    ✅ Configuration management
# │   ├── __init__.py
# │   ├── model_registry.py
# │   ├── prompts.py
# │   ├── output_config.py
# │   └── model_config.py
# ├── parsers/                   ✅ Output parsing
# │   ├── __init__.py
# │   ├── base_parser.py
# │   ├── grounding_parser.py
# │   ├── markdown_parser.py
# │   └── parser_registry.py
# ├── processors/                ✅ File processing
# │   ├── __init__.py
# │   ├── pdf_processor.py
# │   └── image_processor.py
# ├── extractors/                ✅ OCR extraction
# │   ├── __init__.py
# │   ├── base_extractor.py
# │   ├── ollama_extractor.py
# │   └── multipage_processor.py
# ├── visualizers/               ✅ Visualization
# │   ├── __init__.py
# │   └── bbox_visualizer.py
# └── storage/                   ✅ Output management
#     ├── __init__.py
#     ├── directory_builder.py
#     └── output_manager.py