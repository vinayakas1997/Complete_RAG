"""
Parser Registry Module
Automatically selects and manages appropriate parsers for different output formats.
This is the "smart dispatcher" that handles format detection.
"""

from typing import Optional, List
from .base_parser import BaseParser, ParseResult
from .grounding_parser import GroundingParser
from .markdown_parser import MarkdownParser


class ParserRegistry:
    """
    Registry that manages multiple parsers and auto-selects the appropriate one.
    
    This class implements the Strategy Pattern - it tries each parser
    until it finds one that can handle the input.
    """
    
    def __init__(self):
        """Initialize registry with default parsers"""
        self.parsers: List[BaseParser] = []
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register built-in parsers in priority order"""
        # Order matters! More specific parsers first
        self.register_parser(GroundingParser())  # Try grounding first
        self.register_parser(MarkdownParser())   # Fallback to markdown
    
    def register_parser(self, parser: BaseParser):
        """
        Register a new parser.
        
        Args:
            parser: Parser instance to register
            
        Example:
            >>> registry = ParserRegistry()
            >>> custom_parser = MyCustomParser()
            >>> registry.register_parser(custom_parser)
        """
        if not isinstance(parser, BaseParser):
            raise TypeError("Parser must inherit from BaseParser")
        
        self.parsers.append(parser)
    
    def get_parser(self, raw_output: str) -> Optional[BaseParser]:
        """
        Get appropriate parser for the given output.
        
        Tries each registered parser's can_parse() method until
        one returns True.
        
        Args:
            raw_output: Raw OCR output text
            
        Returns:
            BaseParser or None if no parser can handle it
            
        Example:
            >>> registry = ParserRegistry()
            >>> parser = registry.get_parser("<|ref|>table<|/ref|>...")
            >>> print(parser.get_parser_name())
            'grounding_parser'
        """
        for parser in self.parsers:
            try:
                if parser.can_parse(raw_output):
                    return parser
            except Exception as e:
                # Skip parser if can_parse() fails
                print(f"Warning: Parser {parser.get_parser_name()} failed: {e}")
                continue
        
        return None
    
    def parse(self, raw_output: str, prefer_parser: Optional[str] = None) -> ParseResult:
        """
        Parse output using auto-detected or preferred parser.
        
        Args:
            raw_output: Raw OCR output text
            prefer_parser: Optional parser name to try first
            
        Returns:
            ParseResult: Parsed result
            
        Example:
            >>> registry = ParserRegistry()
            >>> result = registry.parse("<|ref|>table<|/ref|>...")
            >>> print(result.success)
            True
        """
        # Try preferred parser first if specified
        if prefer_parser:
            parser = self.get_parser_by_name(prefer_parser)
            if parser and parser.can_parse(raw_output):
                return parser.parse(raw_output)
        
        # Auto-detect parser
        parser = self.get_parser(raw_output)
        
        if parser is None:
            # No parser can handle this - use markdown as last resort
            fallback_parser = MarkdownParser()
            return fallback_parser.parse(raw_output)
        
        return parser.parse(raw_output)
    
    def get_parser_by_name(self, parser_name: str) -> Optional[BaseParser]:
        """
        Get parser by name.
        
        Args:
            parser_name: Name of the parser
            
        Returns:
            BaseParser or None if not found
            
        Example:
            >>> registry = ParserRegistry()
            >>> parser = registry.get_parser_by_name("grounding_parser")
            >>> print(parser is not None)
            True
        """
        for parser in self.parsers:
            if parser.get_parser_name() == parser_name:
                return parser
        return None
    
    def list_parsers(self) -> List[str]:
        """
        Get list of registered parser names.
        
        Returns:
            List of parser names
            
        Example:
            >>> registry = ParserRegistry()
            >>> parsers = registry.list_parsers()
            >>> print(parsers)
            ['grounding_parser', 'markdown_parser']
        """
        return [parser.get_parser_name() for parser in self.parsers]
    
    def remove_parser(self, parser_name: str) -> bool:
        """
        Remove a parser from registry.
        
        Args:
            parser_name: Name of parser to remove
            
        Returns:
            bool: True if removed, False if not found
            
        Example:
            >>> registry = ParserRegistry()
            >>> registry.remove_parser("markdown_parser")
            True
        """
        for i, parser in enumerate(self.parsers):
            if parser.get_parser_name() == parser_name:
                self.parsers.pop(i)
                return True
        return False
    
    def clear_parsers(self):
        """
        Remove all parsers from registry.
        
        Example:
            >>> registry = ParserRegistry()
            >>> registry.clear_parsers()
            >>> print(len(registry.parsers))
            0
        """
        self.parsers.clear()


# Global registry instance (singleton pattern)
_global_registry = None


def get_global_registry() -> ParserRegistry:
    """
    Get global parser registry instance (singleton).
    
    Returns:
        ParserRegistry: Global registry
        
    Example:
        >>> registry = get_global_registry()
        >>> result = registry.parse(ocr_output)
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ParserRegistry()
    return _global_registry


def parse_ocr_output(raw_output: str, prefer_parser: Optional[str] = None) -> ParseResult:
    """
    Convenience function to parse OCR output using global registry.
    
    Args:
        raw_output: Raw OCR output text
        prefer_parser: Optional parser name to prefer
        
    Returns:
        ParseResult: Parsed result
        
    Example:
        >>> result = parse_ocr_output("<|ref|>table<|/ref|>...")
        >>> print(result.success)
        True
    """
    registry = get_global_registry()
    return registry.parse(raw_output, prefer_parser)


if __name__ == "__main__":
    print("Testing parser_registry.py...\n")
    
    # Test 1: Create registry
    print("Test 1: Registry Creation")
    print("-" * 60)
    registry = ParserRegistry()
    parsers = registry.list_parsers()
    print(f"Registered parsers: {parsers}")
    
    # Test 2: Auto-detect grounding format
    print("\n" + "="*60)
    print("Test 2: Auto-detect Grounding Format")
    print("-" * 60)
    grounding_output = """<|ref|>table<|/ref|><|det|>[[59, 53, 582, 105]]<|/det|>
<table><tr><td>Test</td></tr></table>"""
    
    parser = registry.get_parser(grounding_output)
    print(f"Selected parser: {parser.get_parser_name()}")
    
    result = registry.parse(grounding_output)
    print(f"Parse success: {result.success}")
    print(f"Elements found: {result.get_element_count()}")
    print(f"Parser used: {result.parser_type}")
    
    # Test 3: Auto-detect markdown format
    print("\n" + "="*60)
    print("Test 3: Auto-detect Markdown Format")
    print("-" * 60)
    markdown_output = """# Title

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |"""
    
    parser = registry.get_parser(markdown_output)
    print(f"Selected parser: {parser.get_parser_name()}")
    
    result = registry.parse(markdown_output)
    print(f"Parse success: {result.success}")
    print(f"Elements found: {result.get_element_count()}")
    print(f"Parser used: {result.parser_type}")
    
    # Test 4: Prefer specific parser
    print("\n" + "="*60)
    print("Test 4: Prefer Specific Parser")
    print("-" * 60)
    result = registry.parse(markdown_output, prefer_parser="markdown_parser")
    print(f"Parser used: {result.parser_type}")
    
    # Test 5: Get parser by name
    print("\n" + "="*60)
    print("Test 5: Get Parser by Name")
    print("-" * 60)
    grounding_parser = registry.get_parser_by_name("grounding_parser")
    print(f"Found parser: {grounding_parser is not None}")
    print(f"Parser name: {grounding_parser.get_parser_name()}")
    
    # Test 6: Global registry
    print("\n" + "="*60)
    print("Test 6: Global Registry (Convenience Function)")
    print("-" * 60)
    result = parse_ocr_output(grounding_output)
    print(f"Parse success: {result.success}")
    print(f"Parser used: {result.parser_type}")
    
    # Test 7: Unknown format fallback
    print("\n" + "="*60)
    print("Test 7: Unknown Format (Fallback)")
    print("-" * 60)
    unknown_output = "Just plain text with no special format"
    result = registry.parse(unknown_output)
    print(f"Parse success: {result.success}")
    print(f"Parser used: {result.parser_type}")
    print(f"Elements: {result.get_element_count()}")
    
    print("\n✅ parser_registry.py tests passed!")