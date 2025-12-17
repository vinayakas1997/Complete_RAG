"""
Base Parser Module
Abstract base class for all output parsers.
Defines the interface that all parsers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedElement:
    """
    Represents a single parsed element from OCR output.
    
    Attributes:
        element_id: Unique identifier for this element
        element_type: Type of element (table, image, text, sub_title, etc.)
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        content: Extracted content (text, markdown, etc.)
        confidence: Confidence score (0.0 to 1.0), if available
        metadata: Additional metadata specific to element type
    """
    element_id: int
    element_type: str
    bbox: List[int]  # [x1, y1, x2, y2]
    content: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate element data"""
        if len(self.bbox) != 4:
            raise ValueError(f"bbox must have 4 coordinates, got {len(self.bbox)}")
        
        if self.confidence is not None:
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(f"confidence must be between 0 and 1, got {self.confidence}")


@dataclass
class ParseResult:
    """
    Result of parsing OCR output.
    
    Attributes:
        elements: List of parsed elements
        raw_text: Original raw output text
        parser_type: Name of parser used
        success: Whether parsing was successful
        error_message: Error message if parsing failed
        metadata: Additional parsing metadata
    """
    elements: List[ParsedElement]
    raw_text: str
    parser_type: str
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def get_elements_by_type(self, element_type: str) -> List[ParsedElement]:
        """
        Filter elements by type.
        
        Args:
            element_type: Type to filter by (e.g., "table", "image")
            
        Returns:
            List of elements of specified type
            
        Example:
            >>> result = parse_result
            >>> tables = result.get_elements_by_type("table")
            >>> print(len(tables))
            2
        """
        return [elem for elem in self.elements if elem.element_type == element_type]
    
    def get_element_count(self) -> int:
        """
        Get total number of elements.
        
        Returns:
            int: Number of elements
        """
        return len(self.elements)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation
        """
        return {
            "success": self.success,
            "parser_type": self.parser_type,
            "element_count": self.get_element_count(),
            "error_message": self.error_message,
            "elements": [
                {
                    "id": elem.element_id,
                    "type": elem.element_type,
                    "bbox": elem.bbox,
                    "content": elem.content,
                    "confidence": elem.confidence,
                    "metadata": elem.metadata
                }
                for elem in self.elements
            ],
            "metadata": self.metadata
        }


class BaseParser(ABC):
    """
    Abstract base class for OCR output parsers.
    
    All parser implementations must inherit from this class
    and implement the parse() method.
    """
    
    def __init__(self, parser_name: str):
        """
        Initialize parser.
        
        Args:
            parser_name: Name of this parser
        """
        self.parser_name = parser_name
    
    @abstractmethod
    def parse(self, raw_output: str) -> ParseResult:
        """
        Parse raw OCR output into structured elements.
        
        This method MUST be implemented by all subclasses.
        
        Args:
            raw_output: Raw text output from OCR model
            
        Returns:
            ParseResult: Parsed result with elements
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement parse()")
    
    @abstractmethod
    def can_parse(self, raw_output: str) -> bool:
        """
        Check if this parser can handle the given output.
        
        This method MUST be implemented by all subclasses.
        Used by parser registry to auto-select appropriate parser.
        
        Args:
            raw_output: Raw text output to check
            
        Returns:
            bool: True if this parser can handle the output
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement can_parse()")
    
    def get_parser_name(self) -> str:
        """
        Get name of this parser.
        
        Returns:
            str: Parser name
        """
        return self.parser_name
    
    def validate_output(self, raw_output: str) -> bool:
        """
        Validate that output is not empty or malformed.
        
        Args:
            raw_output: Raw output to validate
            
        Returns:
            bool: True if output is valid
        """
        if not raw_output or not isinstance(raw_output, str):
            return False
        
        if len(raw_output.strip()) == 0:
            return False
        
        return True
    
    def create_error_result(self, raw_output: str, error_message: str) -> ParseResult:
        """
        Create a ParseResult for parsing errors.
        
        Args:
            raw_output: Raw output that failed to parse
            error_message: Description of the error
            
        Returns:
            ParseResult: Result with error information
        """
        return ParseResult(
            elements=[],
            raw_text=raw_output,
            parser_type=self.parser_name,
            success=False,
            error_message=error_message
        )


if __name__ == "__main__":
    print("Testing base_parser.py...\n")
    
    # Test 1: Create ParsedElement
    print("Test 1: ParsedElement")
    print("-" * 60)
    element = ParsedElement(
        element_id=1,
        element_type="table",
        bbox=[10, 20, 100, 200],
        content="Sample table content",
        confidence=0.95
    )
    print(f"Element ID: {element.element_id}")
    print(f"Type: {element.element_type}")
    print(f"BBox: {element.bbox}")
    print(f"Confidence: {element.confidence}")
    
    # Test 2: Create ParseResult
    print("\n" + "="*60)
    print("Test 2: ParseResult")
    print("-" * 60)
    elements = [
        ParsedElement(1, "table", [10, 20, 100, 200], "Table 1"),
        ParsedElement(2, "text", [10, 210, 100, 250], "Text 1"),
        ParsedElement(3, "table", [10, 260, 100, 400], "Table 2"),
    ]
    result = ParseResult(
        elements=elements,
        raw_text="Raw output...",
        parser_type="test_parser"
    )
    print(f"Total elements: {result.get_element_count()}")
    tables = result.get_elements_by_type("table")
    print(f"Tables found: {len(tables)}")
    
    # Test 3: Convert to dict
    print("\n" + "="*60)
    print("Test 3: to_dict()")
    print("-" * 60)
    result_dict = result.to_dict()
    print(f"Success: {result_dict['success']}")
    print(f"Element count: {result_dict['element_count']}")
    print(f"First element type: {result_dict['elements'][0]['type']}")
    
    # Test 4: Validation
    print("\n" + "="*60)
    print("Test 4: ParsedElement Validation")
    print("-" * 60)
    try:
        # Invalid bbox (only 3 coordinates)
        bad_element = ParsedElement(1, "table", [10, 20, 100], "content")
        print("✗ Should have failed validation")
    except ValueError as e:
        print(f"✓ Validation caught error: {e}")
    
    try:
        # Invalid confidence (> 1.0)
        bad_element = ParsedElement(1, "table", [10, 20, 100, 200], "content", confidence=1.5)
        print("✗ Should have failed validation")
    except ValueError as e:
        print(f"✓ Validation caught error: {e}")
    
    print("\n✅ base_parser.py tests passed!")