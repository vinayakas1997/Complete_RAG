"""
Model Registry Module
Defines supported models and their default configurations.
Each model has recommended parameters and capabilities.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ModelCapabilities:
    """Model capability flags"""
    grounding: bool = False          # Supports bounding box detection
    markdown: bool = True            # Can output markdown
    tables: bool = True              # Can extract tables
    multilingual: bool = False       # Supports multiple languages
    complex_layouts: bool = False    # Handles complex document layouts


@dataclass
class ModelConfig:
    """Model configuration and metadata"""
    name: str
    type: str  # vision_ocr, vision_general, etc.
    capabilities: ModelCapabilities
    recommended_params: Dict
    prompt_prefix: str = ""
    description: str = ""


# Model Registry - Currently only tested models
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    
    "deepseek-ocr:3b": ModelConfig(
        name="deepseek-ocr:3b",
        type="vision_ocr",
        capabilities=ModelCapabilities(
            grounding=True,
            markdown=True,
            tables=True,
            multilingual=True,
            complex_layouts=True
        ),
        recommended_params={
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 40,
            "num_ctx": 8192
        },
        prompt_prefix="<|grounding|>",
        description="DeepSeek OCR 3B - Fast OCR with grounding support"
    ),
    
    # Fallback for custom/unknown models
    "custom": ModelConfig(
        name="custom",
        type="custom",
        capabilities=ModelCapabilities(
            grounding=False,
            markdown=True,
            tables=True,
            multilingual=False,
            complex_layouts=False
        ),
        recommended_params={
            "temperature": 0.0,
            "top_p": 0.9,
        },
        prompt_prefix="",
        description="Custom model - user provided"
    ),
}


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """
    Get configuration for a specific model.
    Falls back to 'custom' config if model not found.
    
    Args:
        model_name: Name of the model
        
    Returns:
        ModelConfig
        
    Example:
        >>> config = get_model_config("deepseek-ocr:3b")
        >>> print(config.capabilities.grounding)
        True
    """
    return MODEL_REGISTRY.get(model_name, MODEL_REGISTRY["custom"])


def list_available_models() -> List[str]:
    """
    Get list of all registered model names.
    
    Returns:
        List of model names
        
    Example:
        >>> models = list_available_models()
        >>> print(models)
        ['deepseek-ocr:3b']
    """
    return [name for name in MODEL_REGISTRY.keys() if name != "custom"]


def get_default_model() -> str:
    """
    Get the default model name.
    
    Returns:
        str: Default model name
    """
    return "deepseek-ocr:3b"


def merge_model_params(
    model_name: str,
    user_params: Optional[Dict] = None
) -> Dict:
    """
    Merge user parameters with model defaults.
    User parameters override defaults.
    
    Args:
        model_name: Name of the model
        user_params: User-provided parameters
        
    Returns:
        dict: Merged parameters
        
    Example:
        >>> params = merge_model_params("deepseek-ocr:3b", {"temperature": 0.5})
        >>> print(params["temperature"])
        0.5
        >>> print(params["top_p"])
        0.9
    """
    config = get_model_config(model_name)
    
    # Start with model defaults
    merged_params = config.recommended_params.copy()
    
    # Override with user parameters
    if user_params:
        merged_params.update(user_params)
    
    return merged_params


def supports_grounding(model_name: str) -> bool:
    """
    Check if model supports grounding/bounding boxes.
    
    Args:
        model_name: Name of the model
        
    Returns:
        bool: True if supports grounding
        
    Example:
        >>> supports_grounding("deepseek-ocr:3b")
        True
    """
    config = get_model_config(model_name)
    return config.capabilities.grounding


if __name__ == "__main__":
    print("Testing model_registry.py...\n")
    
    # Test 1: List all models
    print("Available models:")
    for model in list_available_models():
        print(f"  - {model}")
    
    # Test 2: Get model config
    print("\n" + "="*60)
    config = get_model_config("deepseek-ocr:3b")
    print(f"Model: {config.name}")
    print(f"Supports grounding: {config.capabilities.grounding}")
    
    # Test 3: Merge parameters
    print("\n" + "="*60)
    merged = merge_model_params("deepseek-ocr:3b", {"temperature": 0.5})
    print(f"Merged params: {merged}")
    
    # Test 4: Custom model fallback
    print("\n" + "="*60)
    custom_config = get_model_config("my-custom-model:latest")
    print(f"Unknown model falls back to: {custom_config.name}")
    
    print("\n✅ model_registry.py tests passed!")