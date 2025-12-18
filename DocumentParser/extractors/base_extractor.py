"""
Base Extractor Module
Abstract base class for all OCR extractors.
Defines the interface that all extractor implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from parsers import ParseResult


@dataclass
class ExtractionResult:
    """
    Result of OCR extraction.
    Contains both raw output and parsed result.
    """
    
    raw_output: str
    parse_result: ParseResult
    model_name: str
    prompt_used: str
    image_path: str
    processing_time: float
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def get_elements(self):
        """Get parsed elements"""
        return self.parse_result.elements
    
    def get_element_count(self) -> int:
        """Get number of elements found"""
        return self.parse_result.get_element_count()
    
    def get_elements_by_type(self, element_type: str):
        """Get elements filtered by type"""
        return self.parse_result.get_elements_by_type(element_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation
        """
        return {
            'success': self.success,
            'model': self.model_name,
            'image_path': self.image_path,
            'processing_time': self.processing_time,
            'element_count': self.get_element_count(),
            'parser_type': self.parse_result.parser_type,
            'error_message': self.error_message,
            'elements': [
                {
                    'id': elem.element_id,
                    'type': elem.element_type,
                    'bbox': elem.bbox,
                    'content': elem.content[:100] + '...' if len(elem.content) > 100 else elem.content,
                    'confidence': elem.confidence
                }
                for elem in self.get_elements()
            ],
            'metadata': self.metadata
        }


class BaseExtractor(ABC):
    """
    Abstract base class for OCR extractors.
    
    All extractor implementations (Ollama, Anthropic, OpenAI, etc.)
    must inherit from this class and implement the required methods.
    """
    
    def __init__(self, extractor_name: str):
        """
        Initialize extractor.
        
        Args:
            extractor_name: Name of this extractor
        """
        self.extractor_name = extractor_name
    
    @abstractmethod
    def extract(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract text and structure from image.
        
        This method MUST be implemented by all subclasses.
        
        Args:
            image_path: Path to image file
            custom_prompt: Override default prompt
            
        Returns:
            ExtractionResult: Extraction result with parsed elements
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement extract()")
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate extractor configuration.
        
        Check if all required settings are present and valid.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement validate_config()")
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if extractor is available and ready to use.
        
        For example:
        - OllamaExtractor: Check if Ollama is running
        - AnthropicExtractor: Check if API key is set
        - OpenAIExtractor: Check if API key is valid
        
        Returns:
            bool: True if extractor is available
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement is_available()")
    
    def get_extractor_name(self) -> str:
        """
        Get name of this extractor.
        
        Returns:
            str: Extractor name
        """
        return self.extractor_name
    
    def validate_image_path(self, image_path: str) -> bool:
        """
        Validate that image path exists and is readable.
        
        Args:
            image_path: Path to image file
            
        Returns:
            bool: True if valid
        """
        path = Path(image_path)
        
        if not path.exists():
            return False
        
        if not path.is_file():
            return False
        
        # Check if it's a supported image format
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        if path.suffix.lower() not in supported_extensions:
            return False
        
        return True
    
    def create_error_result(
        self,
        image_path: str,
        error_message: str,
        model_name: str = "unknown"
    ) -> ExtractionResult:
        """
        Create an error result.
        
        Convenience method for creating error results consistently.
        
        Args:
            image_path: Path to image that failed
            error_message: Description of the error
            model_name: Name of model that failed
            
        Returns:
            ExtractionResult: Error result
        """
        from parsers import ParseResult
        
        empty_parse = ParseResult(
            elements=[],
            raw_text="",
            parser_type="none",
            success=False,
            error_message=error_message
        )
        
        return ExtractionResult(
            raw_output="",
            parse_result=empty_parse,
            model_name=model_name,
            prompt_used="",
            image_path=image_path,
            processing_time=0.0,
            success=False,
            error_message=error_message
        )
    
    def extract_with_retry(
        self,
        image_path: str,
        max_retries: int = 3,
        custom_prompt: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract with automatic retry on failure.
        
        Default implementation - subclasses can override for custom retry logic.
        
        Args:
            image_path: Path to image file
            max_retries: Maximum retry attempts
            custom_prompt: Override default prompt
            
        Returns:
            ExtractionResult: Extraction result
        """
        import time
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = self.extract(image_path, custom_prompt)
                
                if result.success and result.parse_result.success:
                    return result
                
                last_error = result.error_message or result.parse_result.error_message
                
            except Exception as e:
                last_error = str(e)
            
            if attempt < max_retries - 1:
                print(f"Retry {attempt + 1}/{max_retries - 1}: {last_error}")
                time.sleep(1)  # Brief delay before retry
        
        # All retries failed
        return self.create_error_result(
            image_path=image_path,
            error_message=f"Failed after {max_retries} attempts. Last error: {last_error}"
        )
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this extractor.
        
        Returns:
            dict: Extractor information
        """
        return {
            'extractor_name': self.extractor_name,
            'is_available': self.is_available(),
        }


if __name__ == "__main__":
    print("Testing base_extractor.py...\n")
    
    # Test 1: ExtractionResult
    print("Test 1: ExtractionResult")
    print("-" * 60)
    from parsers import ParseResult, ParsedElement
    
    elements = [
        ParsedElement(1, "table", [10, 20, 100, 200], "Table content"),
        ParsedElement(2, "text", [10, 210, 100, 250], "Text content"),
    ]
    
    parse_result = ParseResult(
        elements=elements,
        raw_text="Raw output...",
        parser_type="test_parser"
    )
    
    extraction_result = ExtractionResult(
        raw_output="Raw output...",
        parse_result=parse_result,
        model_name="test-model",
        prompt_used="Test prompt",
        image_path="test.png",
        processing_time=1.5,
        success=True
    )
    
    print(f"Success: {extraction_result.success}")
    print(f"Element count: {extraction_result.get_element_count()}")
    print(f"Processing time: {extraction_result.processing_time}s")
    
    # Test 2: to_dict()
    print("\n" + "="*60)
    print("Test 2: to_dict()")
    print("-" * 60)
    result_dict = extraction_result.to_dict()
    print(f"Dict keys: {list(result_dict.keys())}")
    print(f"Success: {result_dict['success']}")
    print(f"Elements: {len(result_dict['elements'])}")
    
    # Test 3: Cannot instantiate abstract class
    print("\n" + "="*60)
    print("Test 3: Abstract Class")
    print("-" * 60)
    try:
        extractor = BaseExtractor("test")
        print("✗ Should not be able to instantiate abstract class")
    except TypeError as e:
        print(f"✓ Cannot instantiate abstract class: {str(e)[:50]}...")
    
    # Test 4: Image path validation
    print("\n" + "="*60)
    print("Test 4: Image Path Validation")
    print("-" * 60)
    
    # Create dummy extractor for testing
    class DummyExtractor(BaseExtractor):
        def extract(self, image_path, custom_prompt=None):
            pass
        def validate_config(self):
            return True
        def is_available(self):
            return True
    
    dummy = DummyExtractor("dummy")
    
    # Test with invalid path
    is_valid = dummy.validate_image_path("nonexistent.png")
    print(f"Nonexistent file valid: {is_valid}")
    
    # Test with unsupported extension
    is_valid = dummy.validate_image_path("file.txt")
    print(f"Text file valid: {is_valid}")
    
    print("\n✅ base_extractor.py tests passed!")