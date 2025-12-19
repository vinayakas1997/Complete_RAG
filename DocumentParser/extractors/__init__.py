"""
Extractors Package
OCR extraction with support for multiple backends and multi-page documents.
"""

# Base classes
from .base_extractor import (
    BaseExtractor,
    ExtractionResult,
)

# Extractor implementations
from .ollama_extractor import OllamaExtractor
from .huggingface_extractor import HuggingFaceExtractor
# Multi-page processor
from .multipage_processor import (
    MultiPageProcessor,
    PageResult,
    DocumentResult,
)

__all__ = [
    # Base classes
    'BaseExtractor',
    'ExtractionResult',
    # Implementations
    'OllamaExtractor',
    'HuggingFaceExtractor',
    # Multi-page
    'MultiPageProcessor',
    'PageResult',
    'DocumentResult',
]