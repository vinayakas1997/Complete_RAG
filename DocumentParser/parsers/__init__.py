"""
Parsers Package
Handles parsing of different OCR output formats.
"""

# Base classes
from .base_parser import (
    BaseParser,
    ParsedElement,
    ParseResult,
)

# Parser implementations
from .grounding_parser import GroundingParser
from .markdown_parser import MarkdownParser

# Parser registry
from .parser_registry import (
    ParserRegistry,
    get_global_registry,
    parse_ocr_output,
)

__all__ = [
    # Base classes
    'BaseParser',
    'ParsedElement',
    'ParseResult',
    # Parser implementations
    'GroundingParser',
    'MarkdownParser',
    # Registry
    'ParserRegistry',
    'get_global_registry',
    'parse_ocr_output',
]