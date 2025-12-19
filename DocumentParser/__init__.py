"""
DeepSeek OCR - Complete OCR System for Ollama Vision Models
"""

from .main import OllamaOCR, create_ocr
from .config import OCRConfig, create_default_config

from .main import HuggingFaceOCR, create_huggingface_ocr

# Version info
__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Complete OCR system for Ollama-based vision models"

# Public API
__all__ = [
    'OllamaOCR',
    'create_ocr',
# Hugging face
    'HuggingFaceOCR',
    'create_huggingface_ocr'

    'OCRConfig',
    'create_default_config',
]

# Convenience imports for advanced users
def get_version():
    """Get package version"""
    return __version__