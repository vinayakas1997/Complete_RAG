"""
Config Package
Configuration management for DeepSeek OCR system.
"""

# Main configuration class
from .model_config import (
    OCRConfig,
    create_default_config,
    create_fast_config,
    create_quality_config,
    print_config_summary,
)

# Model registry
from .model_registry import (
    ModelConfig,
    ModelCapabilities,
    get_model_config,
    list_available_models,
    get_default_model,
    merge_model_params,
    supports_grounding,
)

# Output configuration
from .output_config import (
    OutputConfig,
    get_default_output_config,
    get_minimal_output_config,
    get_full_output_config,
    validate_output_config,
)

# Prompts
from .prompts import (
    PromptTemplate,
    get_prompt,
    get_prompt_template,
    list_prompts,
    get_prompts_for_model,
    get_default_prompt,
)

__all__ = [
    # Main config
    'OCRConfig',
    'create_default_config',
    'create_fast_config',
    'create_quality_config',
    'print_config_summary',
    # Model registry
    'ModelConfig',
    'ModelCapabilities',
    'get_model_config',
    'list_available_models',
    'get_default_model',
    'merge_model_params',
    'supports_grounding',
    # Output config
    'OutputConfig',
    'get_default_output_config',
    'get_minimal_output_config',
    'get_full_output_config',
    'validate_output_config',
    # Prompts
    'PromptTemplate',
    'get_prompt',
    'get_prompt_template',
    'list_prompts',
    'get_prompts_for_model',
    'get_default_prompt',
]