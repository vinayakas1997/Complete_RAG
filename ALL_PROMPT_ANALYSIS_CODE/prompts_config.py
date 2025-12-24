"""
Prompts Configuration
Define all prompt variants for testing here.

Easy to add/remove/modify prompts without touching other code.
"""

# ========== PROMPT DEFINITIONS ==========

# PROMPTS = [
#     # ===== SIMPLE PROMPTS (Fast, basic) =====
    
#     {
#         "id": 1,
#         "name": "japanese_simple",
#         "prompt": "<image>\n<|grounding|>この文書のテキストと表を抽出。",
#         "description": "Simple Japanese - Extract text and tables",
#         "expected_speed": "Fast (5-15s)",
#         "best_for": "Simple Japanese documents"
#     },
    
#     {
#         "id": 2,
#         "name": "english_simple",
#         "prompt": "<image>\n<|grounding|>Extract text and tables.",
#         "description": "Simple English - Extract text and tables",
#         "expected_speed": "Fast (5-15s)",
#         "best_for": "Simple English documents"
#     },
    
#     # ===== FALLBACK PROMPTS (Safe, prevents hallucination) =====
    
#     {
#         "id": 3,
#         "name": "japanese_fallback",
#         "prompt": "<image>\n<|grounding|>テキストと簡単な表を抽出。複雑な表は画像として扱う。",
#         "description": "Japanese with fallback - Mark complex tables as images",
#         "expected_speed": "Medium (10-20s)",
#         "best_for": "Complex Japanese documents"
#     },
    
#     {
#         "id": 4,
#         "name": "english_fallback",
#         "prompt": "<image>\n<|grounding|>Extract text and simple tables. Mark complex tables as images.",
#         "description": "English with fallback - Mark complex tables as images",
#         "expected_speed": "Medium (10-20s)",
#         "best_for": "Complex English documents"
#     },
    
#     # ===== COMPREHENSIVE PROMPTS (More detailed) =====
    
#     {
#         "id": 5,
#         "name": "japanese_comprehensive",
#         "prompt": "<image>\n<|grounding|>この文書から全てのテキストと表を抽出してください。",
#         "description": "Comprehensive Japanese - Extract all content",
#         "expected_speed": "Medium (15-25s)",
#         "best_for": "Complete Japanese extraction"
#     },
    
#     {
#         "id": 6,
#         "name": "english_comprehensive",
#         "prompt": "<image>\n<|grounding|>Extract all text and tables from this document in markdown format.",
#         "description": "Comprehensive English - Extract all content",
#         "expected_speed": "Medium (15-25s)",
#         "best_for": "Complete English extraction"
#     },
    
#     # ===== MINIMAL PROMPTS (Fastest) =====
    
#     {
#         "id": 7,
#         "name": "japanese_minimal",
#         "prompt": "<image>\n<|grounding|>文書内容を抽出。",
#         "description": "Minimal Japanese - Extract document content",
#         "expected_speed": "Very Fast (3-10s)",
#         "best_for": "Quick extraction"
#     },
    
#     {
#         "id": 8,
#         "name": "english_minimal",
#         "prompt": "<image>\n<|grounding|>Extract document content.",
#         "description": "Minimal English - Extract document content",
#         "expected_speed": "Very Fast (3-10s)",
#         "best_for": "Quick extraction"
#     },
    
#     # ===== SAFE PROMPTS (Prevent getting stuck) =====
    
#     {
#         "id": 9,
#         "name": "japanese_safe",
#         "prompt": "<image>\n<|grounding|>明確な要素のみ抽出。不明確な部分は画像として。",
#         "description": "Safe Japanese - Only extract clear elements",
#         "expected_speed": "Fast (5-15s)",
#         "best_for": "Preventing timeouts"
#     },
    
#     {
#         "id": 10,
#         "name": "english_safe",
#         "prompt": "<image>\n<|grounding|>Extract only clear elements. Mark unclear parts as images.",
#         "description": "Safe English - Only extract clear elements",
#         "expected_speed": "Fast (5-15s)",
#         "best_for": "Preventing timeouts"
#     }
# ]

# version 2 
# PROMPTS = [
#     # ===== ULTRA MINIMAL (Fastest) =====
    
#     {
#         "id": 1,
#         "name": "japanese_minimal",
#         "prompt": "<image>\n<|grounding|>テキストと表を抽出。",
#         "description": "Minimal Japanese - Extract text and tables",
#         "expected_speed": "Very Fast (5-15s)",
#         "best_for": "Quick extraction"
#     },
    
#     {
#         "id": 2,
#         "name": "english_minimal",
#         "prompt": "<image>\n<|grounding|>Extract text and tables.",
#         "description": "Minimal English - Extract text and tables",
#         "expected_speed": "Very Fast (5-15s)",
#         "best_for": "Quick extraction"
#     },
    
#     # ===== SIMPLE WITH FALLBACK (Safe) =====
    
#     {
#         "id": 3,
#         "name": "japanese_safe",
#         "prompt": "<image>\n<|grounding|>テキストと表を抽出。不明確な部分は画像として扱う。",
#         "description": "Japanese safe - Mark unclear as image",
#         "expected_speed": "Fast (10-20s)",
#         "best_for": "Preventing hallucination"
#     },
    
#     {
#         "id": 4,
#         "name": "english_safe",
#         "prompt": "<image>\n<|grounding|>Extract text and tables. Mark unclear parts as images.",
#         "description": "English safe - Mark unclear as image",
#         "expected_speed": "Fast (10-20s)",
#         "best_for": "Preventing hallucination"
#     },
    
#     # ===== TABLE-FOCUSED (Simple) =====
    
#     {
#         "id": 5,
#         "name": "japanese_tables",
#         "prompt": "<image>\n<|grounding|>表とテキストを抽出。",
#         "description": "Japanese tables - Tables and text",
#         "expected_speed": "Fast (10-20s)",
#         "best_for": "Documents with tables"
#     },
    
#     {
#         "id": 6,
#         "name": "english_tables",
#         "prompt": "<image>\n<|grounding|>Extract tables and text.",
#         "description": "English tables - Tables and text",
#         "expected_speed": "Fast (10-20s)",
#         "best_for": "Documents with tables"
#     },
    
#     # ===== CONSERVATIVE (Most reliable) =====
    
#     {
#         "id": 7,
#         "name": "japanese_conservative",
#         "prompt": "<image>\n<|grounding|>明確な要素のみ抽出。",
#         "description": "Japanese conservative - Only clear elements",
#         "expected_speed": "Very Fast (5-15s)",
#         "best_for": "Maximum reliability"
#     },
    
#     {
#         "id": 8,
#         "name": "english_conservative",
#         "prompt": "<image>\n<|grounding|>Extract only clear elements.",
#         "description": "English conservative - Only clear elements",
#         "expected_speed": "Very Fast (5-15s)",
#         "best_for": "Maximum reliability"
#     }
# ]

# version 3 official document checking and testing prompts 
# PROMPTS = [
#     # ===== NEW - OFFICIAL PATTERNS (For complex pages) =====
    
#     {
#         "id": 9,
#         "name": "markdown_convert",
#         "prompt": "<image>\n<|grounding|>Convert the document to markdown.",
#         "description": "Official markdown conversion",
#         "expected_speed": "Medium (15-30s)",
#         "best_for": "Complex tables, structured documents"
#     },
    
#     {
#         "id": 10,
#         "name": "markdown_tables",
#         "prompt": "<image>\n<|grounding|>Convert the document to markdown. Include all table structures.",
#         "description": "Markdown with table emphasis",
#         "expected_speed": "Medium (20-40s)",
#         "best_for": "Complex nested tables"
#     },
    
#     {
#         "id": 11,
#         "name": "ocr_document",
#         "prompt": "<image>\n<|grounding|>OCR this image.",
#         "description": "Simple OCR",
#         "expected_speed": "Fast (5-15s)",
#         "best_for": "Text-heavy documents"
#     },
    
#     {
#         "id": 12,
#         "name": "extract_complete",
#         "prompt": "<image>\n<|grounding|>Extract all text and tables. Include complete table structures.",
#         "description": "Complete extraction (like yesterday)",
#         "expected_speed": "Medium (20-40s)",
#         "best_for": "Complex tables like Image 2, 3"
#     },
# ]

# version 4 for the qwen3-vl:latest
PROMPTS = [
    # ===== SIMPLE EXTRACTION =====
    
    {
        "id": 1,
        "name": "qwen_simple",
        "prompt": "Extract all text and tables from this image.",
        "description": "Simple extraction",
        "expected_speed": "Unknown (testing)",
        "best_for": "General documents"
    },
    
    {
        "id": 2,
        "name": "qwen_tables",
        "prompt": "Extract all tables and text from this image. Include table structures.",
        "description": "Table-focused",
        "expected_speed": "Unknown (testing)",
        "best_for": "Table-heavy documents"
    },
    
    {
        "id": 3,
        "name": "qwen_markdown",
        "prompt": "Convert this image to markdown format. Include all text and tables.",
        "description": "Markdown conversion",
        "expected_speed": "Unknown (testing)",
        "best_for": "Structured documents"
    },
    
    {
        "id": 4,
        "name": "qwen_japanese",
        "prompt": "この画像から全てのテキストと表を抽出してください。",
        "description": "Japanese extraction",
        "expected_speed": "Unknown (testing)",
        "best_for": "Japanese documents"
    },
    
    {
        "id": 5,
        "name": "qwen_detailed",
        "prompt": "Extract all content from this image including text, tables, and structured data. Preserve document layout.",
        "description": "Detailed extraction",
        "expected_speed": "Unknown (testing)",
        "best_for": "Complex documents"
    },
    
    {
        "id": 6,
        "name": "qwen_safe",
        "prompt": "Extract text and tables from this image. If structure is unclear, describe what you see.",
        "description": "Safe extraction with fallback",
        "expected_speed": "Unknown (testing)",
        "best_for": "Complex unclear documents"
    },
]


# ========== HELPER FUNCTIONS ==========

def get_all_prompts():
    """
    Get all prompts.
    
    Returns:
        list: List of all prompt dictionaries
    """
    return PROMPTS


def get_prompt_by_id(prompt_id):
    """
    Get specific prompt by ID.
    
    Args:
        prompt_id (int): Prompt ID (1-10)
        
    Returns:
        dict: Prompt dictionary or None if not found
    """
    for prompt in PROMPTS:
        if prompt['id'] == prompt_id:
            return prompt
    return None


def get_prompt_by_name(prompt_name):
    """
    Get specific prompt by name.
    
    Args:
        prompt_name (str): Prompt name
        
    Returns:
        dict: Prompt dictionary or None if not found
    """
    for prompt in PROMPTS:
        if prompt['name'] == prompt_name:
            return prompt
    return None


def get_prompt_count():
    """
    Get total number of prompts.
    
    Returns:
        int: Number of prompts
    """
    return len(PROMPTS)


def get_prompt_names():
    """
    Get list of all prompt names.
    
    Returns:
        list: List of prompt names
    """
    return [p['name'] for p in PROMPTS]


def print_prompts_summary():
    """Print summary of all prompts."""
    print("="*80)
    print("AVAILABLE PROMPTS")
    print("="*80)
    print(f"\nTotal prompts: {get_prompt_count()}")
    print("\n" + "-"*80)
    
    for prompt in PROMPTS:
        print(f"\n{prompt['id']:2d}. {prompt['name']}")
        print(f"    {prompt['description']}")
        print(f"    Speed: {prompt['expected_speed']}")
        print(f"    Best for: {prompt['best_for']}")
    
    print("\n" + "="*80)


# ========== TESTING ==========

if __name__ == "__main__":
    # Test the configuration
    print_prompts_summary()
    
    # Test functions
    print("\n" + "="*80)
    print("TESTING HELPER FUNCTIONS")
    print("="*80)
    
    # Get by ID
    prompt = get_prompt_by_id(1)
    print(f"\nPrompt ID 1: {prompt['name']}")
    print(f"Text: {prompt['prompt'][:50]}...")
    
    # Get by name
    prompt = get_prompt_by_name("japanese_fallback")
    print(f"\nPrompt 'japanese_fallback' ID: {prompt['id']}")
    
    # Get all names
    names = get_prompt_names()
    print(f"\nAll prompt names: {names[:3]}... (showing first 3)")
    
    print("\n✓ Configuration file working correctly!\n")