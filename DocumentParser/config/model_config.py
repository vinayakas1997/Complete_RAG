"""
Model Configuration Module
Main configuration class for DeepSeek OCR.
This is what users interact with to configure the system.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field

from .model_registry import (
    get_model_config,
    get_default_model,
    merge_model_params,
    supports_grounding
)
from .output_config import OutputConfig, get_default_output_config
from .prompts import get_default_prompt, get_prompt


@dataclass
class OCRConfig:
    """
    Main configuration for OCR system.
    Combines model, prompt, and output settings.
    """
    
    # ========== Model Configuration ==========
    model_name: str = field(default_factory=get_default_model)
    host: str = "http://localhost:11434"
    
    # Model parameters (None = use model defaults)
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    num_ctx: Optional[int] = None
    
    # Custom parameters override
    model_params: Optional[Dict] = None
    
    # ========== Prompt Configuration ==========
    use_grounding: bool = True
    custom_prompt: Optional[str] = None
    prompt_key: str = "grounding_markdown_v1.0"  # From prompts.py
    
    # ========== Output Configuration ==========
    output_config: OutputConfig = field(default_factory=get_default_output_config)
    
    # Quick output overrides (override output_config settings)
    output_dir: Optional[str] = None
    save_annotation_copy: Optional[bool] = None
    
    # ========== Processing Configuration ==========
    preprocess_image: bool = False
    parallel_processing: bool = False
    max_workers: int = 4
    
    # ========== Visualization Configuration ==========
    show_labels: bool = True
    box_width: int = 3
    color_scheme: str = "default"  # default, colorblind, grayscale
    
    # ========== Quality Configuration ==========
    validate_output: bool = True
    retry_on_failure: bool = True
    max_retries: int = 3
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Apply quick overrides to output_config
        if self.output_dir is not None:
            self.output_config.output_base_dir = self.output_dir
        
        if self.save_annotation_copy is not None:
            self.output_config.save_visualizations = self.save_annotation_copy
            self.output_config.save_per_page["annotated_image"] = self.save_annotation_copy
    
    def get_merged_model_params(self) -> Dict:
        """
        Get final model parameters after merging defaults with user overrides.
        
        Returns:
            dict: Merged parameters
            
        Example:
            >>> config = OCRConfig(temperature=0.5)
            >>> params = config.get_merged_model_params()
            >>> print(params["temperature"])
            0.5
        """
        # Start with model defaults
        params = merge_model_params(self.model_name, self.model_params)
        
        # Apply individual parameter overrides
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.top_k is not None:
            params["top_k"] = self.top_k
        if self.num_ctx is not None:
            params["num_ctx"] = self.num_ctx
        
        return params
    
    def get_prompt(self) -> str:
        """
        Get the prompt to use for OCR.
        
        Priority:
        1. custom_prompt (if provided)
        2. prompt from prompt_key
        3. default prompt based on use_grounding
        
        Returns:
            str: Prompt text
            
        Example:
            >>> config = OCRConfig()
            >>> prompt = config.get_prompt()
            >>> print(prompt)
            '<|grounding|>Convert the document to markdown.'
        """
        if self.custom_prompt:
            return self.custom_prompt
        
        if self.prompt_key:
            return get_prompt(self.prompt_key)
        
        return get_default_prompt(self.use_grounding)
    
    def supports_grounding(self) -> bool:
        """
        Check if current model supports grounding.
        
        Returns:
            bool: True if grounding is supported
            
        Example:
            >>> config = OCRConfig(model_name="deepseek-ocr:3b")
            >>> config.supports_grounding()
            True
        """
        return supports_grounding(self.model_name)
    
    def validate(self) -> bool:
        """
        Validate configuration for common issues.
        
        Returns:
            bool: True if valid
            
        Raises:
            ValueError: If configuration is invalid
            
        Example:
            >>> config = OCRConfig()
            >>> config.validate()
            True
        """
        # Check if grounding is requested but not supported
        if self.use_grounding and not self.supports_grounding():
            raise ValueError(
                f"Model '{self.model_name}' does not support grounding. "
                f"Set use_grounding=False or use a different model."
            )
        
        # Validate output config
        from .output_config import validate_output_config
        validate_output_config(self.output_config)
        
        # Check workers count
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        
        return True


def create_default_config() -> OCRConfig:
    """
    Create default OCR configuration.
    
    Returns:
        OCRConfig: Default configuration
        
    Example:
        >>> config = create_default_config()
        >>> print(config.model_name)
        'deepseek-ocr:3b'
    """
    return OCRConfig()


def create_fast_config() -> OCRConfig:
    """
    Create configuration optimized for speed.
    
    Returns:
        OCRConfig: Fast processing configuration
        
    Example:
        >>> config = create_fast_config()
        >>> print(config.parallel_processing)
        True
    """
    from .output_config import get_minimal_output_config
    
    return OCRConfig(
        output_config=get_minimal_output_config(),
        parallel_processing=True,
        max_workers=4,
        preprocess_image=False,
        validate_output=False
    )


def create_quality_config() -> OCRConfig:
    """
    Create configuration optimized for quality.
    
    Returns:
        OCRConfig: High quality configuration
        
    Example:
        >>> config = create_quality_config()
        >>> print(config.retry_on_failure)
        True
    """
    from .output_config import get_full_output_config
    
    return OCRConfig(
        output_config=get_full_output_config(),
        preprocess_image=True,
        validate_output=True,
        retry_on_failure=True,
        max_retries=3
    )


def print_config_summary(config: OCRConfig):
    """
    Print configuration summary.
    
    Args:
        config: OCR configuration
        
    Example:
        >>> config = create_default_config()
        >>> print_config_summary(config)
        OCR Configuration Summary
        =========================
        Model: deepseek-ocr:3b
        ...
    """
    print("\nOCR Configuration Summary")
    print("=" * 60)
    
    print(f"Model: {config.model_name}")
    print(f"Host: {config.host}")
    print(f"Use Grounding: {config.use_grounding}")
    
    print(f"\nModel Parameters:")
    params = config.get_merged_model_params()
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    print(f"\nPrompt:")
    prompt = config.get_prompt()
    print(f"  {prompt[:60]}..." if len(prompt) > 60 else f"  {prompt}")
    
    print(f"\nOutput:")
    print(f"  Directory: {config.output_config.output_base_dir}")
    print(f"  Save Visualizations: {config.output_config.save_visualizations}")
    print(f"  Create Combined: {config.output_config.create_combined}")
    
    print(f"\nProcessing:")
    print(f"  Parallel: {config.parallel_processing}")
    print(f"  Workers: {config.max_workers}")
    print(f"  Preprocess: {config.preprocess_image}")
    
    print("=" * 60)


if __name__ == "__main__":
    print("Testing model_config.py...\n")
    
    # Test 1: Default config
    print("Test 1: Default Configuration")
    print("-" * 60)
    config = create_default_config()
    print(f"Model: {config.model_name}")
    print(f"Use grounding: {config.use_grounding}")
    print(f"Prompt: {config.get_prompt()[:50]}...")
    
    # Test 2: Merged parameters
    print("\n" + "="*60)
    print("Test 2: Parameter Merging")
    print("-" * 60)
    config_custom = OCRConfig(temperature=0.5, top_p=0.95)
    params = config_custom.get_merged_model_params()
    print(f"Temperature: {params['temperature']}")
    print(f"Top P: {params['top_p']}")
    
    # Test 3: Fast config
    print("\n" + "="*60)
    print("Test 3: Fast Configuration")
    print("-" * 60)
    fast_config = create_fast_config()
    print(f"Parallel: {fast_config.parallel_processing}")
    print(f"Save raw: {fast_config.output_config.save_per_page['raw_output']}")
    
    # Test 4: Quality config
    print("\n" + "="*60)
    print("Test 4: Quality Configuration")
    print("-" * 60)
    quality_config = create_quality_config()
    print(f"Retry on failure: {quality_config.retry_on_failure}")
    print(f"Save annotated: {quality_config.output_config.save_per_page['annotated_image']}")
    
    # Test 5: Validation
    print("\n" + "="*60)
    print("Test 5: Validation")
    print("-" * 60)
    try:
        config.validate()
        print("✓ Configuration is valid")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")
    
    # Test 6: Print summary
    print_config_summary(config)
    
    print("\n✅ model_config.py tests passed!")