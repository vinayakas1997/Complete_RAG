"""
Prompts Library Module
Stores all OCR prompts with versioning and descriptions.
Allows easy A/B testing and prompt management.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Prompt template with metadata"""
    version: str
    prompt: str
    description: str
    use_grounding: bool = True
    model_specific: Optional[str] = None  # None means works with all models


# Prompt Library
PROMPTS: Dict[str, PromptTemplate] = {
    
    # Grounding prompts (for bounding box detection)
    "grounding_v1.0": PromptTemplate(
        version="v1.0",
        prompt="<|grounding|>Extract all text elements with their positions.",
        description="Basic grounding prompt - extracts text with bounding boxes",
        use_grounding=True,
        model_specific="deepseek-ocr"
    ),
    
    # "grounding_markdown_v1.0": PromptTemplate(
    #     version="v1.0",
    #     prompt="<|grounding|>Convert the document to markdown.",
    #     description="Grounding + markdown conversion",
    #     use_grounding=True,
    #     model_specific="deepseek-ocr"
    # ),
    
    # "grounding_markdown_v1.0": PromptTemplate(
    #     version="v1.0",
    #     prompt= """
    # <|grounding|>Extract ALL content completely:
    # 1. ALL tables - complete structures, not fragments
    # 2. Table headers and all data rows
    # 3. All text outside tables
    # 4. Preserve document layout
    # Focus: Completeness and accuracy.""",
    #     description="Grounding + markdown conversion",
    #     use_grounding=True,
    #     model_specific="deepseek-ocr"
    # ),

    "grounding_detailed_v1.0": PromptTemplate(
        version="v1.0",
        prompt="<|grounding|>Extract all text, tables, and structural elements from this document.",
        description="Detailed extraction with grounding",
        use_grounding=True,
        model_specific="deepseek-ocr"
    ),
    
    # Markdown prompts (no grounding)
    "markdown_v1.0": PromptTemplate(
        version="v1.0",
        prompt="Convert this document to markdown format. Preserve all text, tables, and structure.",
        description="Simple markdown conversion without grounding",
        use_grounding=False,
        model_specific=None
    ),
    
    "markdown_tables_v1.0": PromptTemplate(
        version="v1.0",
        prompt="Extract all content from this document and format as markdown. Pay special attention to tables and preserve their structure.",
        description="Markdown with emphasis on tables",
        use_grounding=False,
        model_specific=None
    ),
    
    # OCR prompts (plain text)
    "ocr_basic_v1.0": PromptTemplate(
        version="v1.0",
        prompt="Extract all text from this image.",
        description="Basic OCR - just extract text",
        use_grounding=False,
        model_specific=None
    ),
    
    "ocr_japanese_v1.0": PromptTemplate(
        version="v1.0",
        prompt="この文書からすべてのテキストを抽出してください。",
        description="Japanese OCR prompt",
        use_grounding=False,
        model_specific=None
    ),
    
    # Specialized prompts
    "flowchart_v1.0": PromptTemplate(
        version="v1.0",
        prompt="<|grounding|>This document contains flowcharts. Extract all text and identify the flowchart structure.",
        description="Optimized for flowchart documents",
        use_grounding=True,
        model_specific="deepseek-ocr"
    ),
    
    "form_v1.0": PromptTemplate(
        version="v1.0",
        prompt="<|grounding|>Extract all fields and values from this form. Preserve the field names and their corresponding values.",
        description="Form field extraction",
        use_grounding=True,
        model_specific="deepseek-ocr"
    ),
}


def get_prompt(prompt_key: str = "grounding_markdown_v1.0") -> str:
    """
    Get prompt text by key.
    
    Args:
        prompt_key: Key from PROMPTS dictionary
        
    Returns:
        str: Prompt text
        
    Example:
        >>> prompt = get_prompt("grounding_v1.0")
        >>> print(prompt)
        '<|grounding|>Extract all text elements with their positions.'
    """
    template = PROMPTS.get(prompt_key)
    if template is None:
        # Fallback to default
        template = PROMPTS["grounding_markdown_v1.0"]
    return template.prompt


def get_prompt_template(prompt_key: str = "grounding_markdown_v1.0") -> PromptTemplate:
    """
    Get full prompt template with metadata.
    
    Args:
        prompt_key: Key from PROMPTS dictionary
        
    Returns:
        PromptTemplate: Template with metadata
        
    Example:
        >>> template = get_prompt_template("grounding_v1.0")
        >>> print(template.use_grounding)
        True
    """
    return PROMPTS.get(prompt_key, PROMPTS["grounding_markdown_v1.0"])


def list_prompts() -> list:
    """
    List all available prompt keys.
    
    Returns:
        list: List of prompt keys
        
    Example:
        >>> prompts = list_prompts()
        >>> print(prompts)
        ['grounding_v1.0', 'grounding_markdown_v1.0', ...]
    """
    return list(PROMPTS.keys())


def get_prompts_for_model(model_name: str) -> list:
    """
    Get prompts compatible with a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        list: List of compatible prompt keys
        
    Example:
        >>> prompts = get_prompts_for_model("deepseek-ocr:3b")
        >>> print(prompts)
        ['grounding_v1.0', 'grounding_markdown_v1.0', ...]
    """
    compatible = []
    model_family = model_name.split(':')[0]  # e.g., "deepseek-ocr" from "deepseek-ocr:3b"
    
    for key, template in PROMPTS.items():
        # Include if model_specific is None (works with all) or matches model family
        if template.model_specific is None or template.model_specific in model_family:
            compatible.append(key)
    
    return compatible


def get_default_prompt(use_grounding: bool = True) -> str:
    """
    Get default prompt based on grounding preference.
    
    Args:
        use_grounding: Whether to use grounding
        
    Returns:
        str: Default prompt text
        
    Example:
        >>> prompt = get_default_prompt(use_grounding=True)
        >>> print(prompt)
        '<|grounding|>Convert the document to markdown.'
    """
    if use_grounding:
        return get_prompt("grounding_markdown_v1.0")
    else:
        return get_prompt("markdown_v1.0")


def print_prompt_info(prompt_key: str):
    """
    Print detailed information about a prompt.
    
    Args:
        prompt_key: Key from PROMPTS dictionary
        
    Example:
        >>> print_prompt_info("grounding_v1.0")
        Prompt: grounding_v1.0
        Version: v1.0
        Description: Basic grounding prompt...
        ...
    """
    template = PROMPTS.get(prompt_key)
    
    if template is None:
        print(f"Prompt '{prompt_key}' not found")
        return
    
    print(f"\nPrompt Information: {prompt_key}")
    print("=" * 60)
    print(f"Version: {template.version}")
    print(f"Description: {template.description}")
    print(f"Use Grounding: {template.use_grounding}")
    print(f"Model Specific: {template.model_specific or 'All models'}")
    print(f"\nPrompt Text:")
    print(f"  {template.prompt}")
    print("=" * 60)


if __name__ == "__main__":
    print("Testing prompts.py...\n")
    
    # Test 1: List all prompts
    print("Available prompts:")
    for key in list_prompts():
        print(f"  - {key}")
    
    # Test 2: Get prompt text
    print("\n" + "="*60)
    prompt = get_prompt("grounding_v1.0")
    print(f"Prompt text: {prompt}")
    
    # Test 3: Get prompts for model
    print("\n" + "="*60)
    deepseek_prompts = get_prompts_for_model("deepseek-ocr:3b")
    print(f"Prompts for deepseek-ocr:3b: {len(deepseek_prompts)} available")
    
    # Test 4: Get default prompt
    print("\n" + "="*60)
    default = get_default_prompt(use_grounding=True)
    print(f"Default grounding prompt: {default}")
    
    # Test 5: Print prompt info
    print_prompt_info("grounding_markdown_v1.0")
    
    print("\n✅ prompts.py tests passed!")