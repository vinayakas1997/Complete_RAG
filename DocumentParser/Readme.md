# DocumentParser - Complete Developer Documentation

**A Production-Grade OCR System for Document Processing with Vision Language Models**

Version: 1.0.0  
Last Updated: December 2024

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Architecture & Data Flow](#2-architecture--data-flow)
3. [Configuration System](#3-configuration-system)
4. [Processing Modes](#4-processing-modes)
5. [Adding New Extractors](#5-adding-new-extractors)
6. [Adding New Models](#6-adding-new-models)
7. [Module Deep Dive](#7-module-deep-dive)
8. [Extension Points](#8-extension-points)
9. [Troubleshooting Guide](#9-troubleshooting-guide)
10. [Best Practices](#10-best-practices)

---

## 1. High-Level Overview

### 1.1 What is DocumentParser?

DocumentParser is a modular OCR system that converts documents (PDFs, images) into structured, searchable data using Vision Language Models (VLMs). It supports:

- ✅ **Multi-page PDF processing**
- ✅ **Grounding detection** (bounding boxes)
- ✅ **Multiple output formats** (Markdown, JSON, images)
- ✅ **Visual annotations** (boxes with labels)
- ✅ **Extensible architecture** (easy to add new models)

### 1.2 Project Structure

```
DocumentParser/
├── __init__.py              # Package entry point
├── main.py                  # Main OllamaOCR class (user-facing API)
│
├── config/                  # Configuration management
│   ├── model_registry.py    # Model definitions
│   ├── prompts.py          # Prompt templates
│   ├── output_config.py    # Output settings
│   └── model_config.py     # OCR configuration
│
├── utils/                   # Utility functions
│   ├── file_utils.py       # File operations
│   └── network_utils.py    # Network/Ollama helpers
│
├── parsers/                 # Output parsing
│   ├── base_parser.py      # Abstract parser
│   ├── grounding_parser.py # Parse <|ref|><|det|> format
│   ├── markdown_parser.py  # Parse plain markdown
│   └── parser_registry.py  # Auto-detection
│
├── processors/              # File preprocessing
│   ├── pdf_processor.py    # PDF → Images
│   └── image_processor.py  # Image preprocessing
│
├── extractors/              # OCR extraction
│   ├── base_extractor.py   # Abstract extractor
│   ├── ollama_extractor.py # Ollama backend
│   └── multipage_processor.py # Document orchestration
│
├── visualizers/             # Visualization
│   └── bbox_visualizer.py  # Draw bounding boxes
│
└── storage/                 # Output management
    ├── directory_builder.py # Create folder structure
    └── output_manager.py    # Save results
```

### 1.3 Key Concepts

#### **Extractor**
Communicates with the OCR model (Ollama, HuggingFace, etc.) and returns raw text + bounding boxes.

#### **Parser**
Converts raw model output into structured data (elements with types, bboxes, content).

#### **Processor**
Handles file conversions (PDF → images) and preprocessing.

#### **Visualizer**
Creates annotated images showing detected elements.

#### **Output Manager**
Saves results in organized directory structure.

---

## 2. Architecture & Data Flow

### 2.1 Complete Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                                │
│              document.pdf or image.png                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   OllamaOCR.process()                        │
│                    (main.py)                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              MultiPageProcessor                              │
│           (extractors/multipage_processor.py)                │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │ 1. Validate file exists                          │      │
│  │ 2. Create output directory structure             │      │
│  │ 3. Detect file type (PDF vs Image)               │      │
│  └──────────────────────┬───────────────────────────┘      │
│                         │                                    │
│         ┌───────────────┴───────────────┐                   │
│         │                               │                   │
│         ▼                               ▼                   │
│    [PDF Branch]                    [Image Branch]           │
│         │                               │                   │
│         ▼                               │                   │
│  ┌──────────────┐                      │                   │
│  │ PDFProcessor │                      │                   │
│  │ Convert to   │                      │                   │
│  │ images (DPI) │                      │                   │
│  └──────┬───────┘                      │                   │
│         │                               │                   │
│         └───────────────┬───────────────┘                   │
│                         │                                    │
│                         ▼                                    │
│              [List of image paths]                          │
│                         │                                    │
│         ┌───────────────┴───────────────┐                   │
│         │     FOR EACH PAGE/IMAGE       │                   │
│         │                               │                   │
│         ▼                               │                   │
│  ┌──────────────────────────────────┐  │                   │
│  │     _process_page()               │  │                   │
│  │                                   │  │                   │
│  │  1. Resize to 1024×1024          │  │                   │
│  │  2. Call OllamaExtractor         │◄─┘                   │
│  │  3. Parse output                  │                      │
│  │  4. Save results                  │                      │
│  │  5. Create annotations            │                      │
│  └──────────────┬────────────────────┘                      │
│                 │                                            │
│                 ▼                                            │
│         [PageResult objects]                                │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────┐                      │
│  │  Combine all pages (if >1 page)  │                      │
│  │  - full_document.md               │                      │
│  │  - full_document.json             │                      │
│  └──────────────┬────────────────────┘                      │
│                 │                                            │
│                 ▼                                            │
│         [DocumentResult]                                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT STRUCTURE                          │
│                                                              │
│  output/document_name/                                       │
│  ├── pages/                                                  │
│  │   ├── page_001/                                          │
│  │   │   ├── raw_output.txt          ← Model's raw response│
│  │   │   ├── grounding.json          ← Parsed elements     │
│  │   │   ├── page_001.md             ← Markdown format     │
│  │   │   ├── page_001_original.png   ← 1024×1024 original  │
│  │   │   ├── page_001_annotated.png  ← With bboxes         │
│  │   │   └── page_001_comparison.png ← Side-by-side        │
│  │   └── page_002/ ...                                      │
│  ├── combined/                                               │
│  │   ├── full_document.md            ← All pages combined  │
│  │   └── full_document.json                                 │
│  └── metadata.json                   ← Processing stats    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Single Page Processing Detail

```
┌────────────────────────────────────────────────────────────┐
│                    _process_page()                          │
└────────────────────┬───────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   [STEP 1]               [STEP 2]
   Resize Image           Extract OCR
        │                         │
        │  Original: 3509×2480   │
        │  Resized:  1024×1024   │
        │                         │
        └────────────┬────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   OllamaExtractor     │
         │   .extract()          │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  ollama.generate()    │
         │  - model: deepseek    │
         │  - prompt: grounding  │
         │  - image: 1024×1024   │
         │  - temp: 0.0          │
         │  - tokens: 8192       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │    Raw Output         │
         │  <|ref|>title         │
         │  <|/ref|><|det|>      │
         │  [[425,100,570,120]]  │
         │  <|/det|>...          │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  parse_ocr_output()   │
         │  Auto-detect format:  │
         │  - Grounding?         │
         │  - Plain markdown?    │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │    ParseResult        │
         │  Elements:            │
         │   - ID: 1             │
         │   - Type: title       │
         │   - BBox: [425,...]   │
         │   - Content: "..."    │
         └───────────┬───────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   [STEP 3]               [STEP 4]
   Save Results          Visualize
        │                         │
        ▼                         ▼
   OutputManager         BBoxVisualizer
        │                         │
        ├─ raw_output.txt         ├─ annotated.png
        ├─ grounding.json         └─ comparison.png
        └─ page_001.md
```

---

## 3. Configuration System

### 3.1 Configuration Hierarchy

```
OCRConfig (Top Level)
    │
    ├─ model_name: str
    ├─ host: str
    ├─ temperature: float
    ├─ context_length: int
    ├─ use_grounding: bool
    │
    └─ output_config: OutputConfig
            │
            ├─ output_base_dir: str
            ├─ folder_naming: str
            ├─ save_per_page: dict
            ├─ create_combined: bool
            ├─ create_comparison: bool
            └─ save_metadata: bool
```

### 3.2 Configuration Presets

#### **Default Config** (Balanced)
```python
from DocumentParser import OllamaOCR

ocr = OllamaOCR()  # Uses default config

# Equivalent to:
config = OCRConfig(
    model_name="deepseek-ocr:3b",
    temperature=0.0,
    use_grounding=True,
    output_config=OutputConfig(
        save_per_page={
            'raw_output': True,
            'grounding_json': True,
            'annotated_image': False,  # Default: disabled
            'markdown': False
        }
    )
)
```

**Output:**
```
output/document/
└── pages/page_001/
    ├── raw_output.txt      ✅
    └── grounding.json      ✅
```

---

#### **Full Output Config** (Everything Enabled)
```python
from DocumentParser import OllamaOCR
from DocumentParser.config import get_full_output_config, OCRConfig

output_config = get_full_output_config()
config = OCRConfig(output_config=output_config)
ocr = OllamaOCR(config=config)
```

**Output:**
```
output/document/
├── pages/
│   └── page_001/
│       ├── raw_output.txt         ✅
│       ├── grounding.json         ✅
│       ├── page_001.md            ✅
│       ├── page_001_original.png  ✅
│       ├── page_001_annotated.png ✅
│       └── page_001_comparison.png ✅
├── combined/
│   ├── full_document.md           ✅
│   └── full_document.json         ✅
└── metadata.json                   ✅
```

---

#### **Minimal Config** (Raw Text Only)
```python
from DocumentParser.config import get_minimal_output_config

output_config = get_minimal_output_config()
config = OCRConfig(output_config=output_config)
ocr = OllamaOCR(config=config)
```

**Output:**
```
output/document/
└── pages/page_001/
    └── raw_output.txt      ✅ (Only this!)
```

---

#### **Quality Mode** (Best Results, Slower)
```python
ocr = OllamaOCR(quality_mode=True)

# Uses:
# - Higher context window
# - More processing time
# - Better accuracy
```

---

### 3.3 Custom Configuration

```python
from DocumentParser.config import OutputConfig, OCRConfig

# Create custom output config
custom_output = OutputConfig(
    output_base_dir="my_results",          # Custom output folder
    folder_naming="timestamp",             # Add timestamp to folder names
    
    save_per_page={
        'raw_output': True,
        'grounding_json': True,
        'annotated_image': True,           # Enable annotations
        'markdown': True,                  # Enable markdown
        'original_image': False            # Don't save original
    },
    
    create_combined=True,                  # Combine multi-page
    combined_formats=["markdown", "json"], # Both formats
    
    create_comparison=True,                # Side-by-side images
    save_metadata=True,                    # Processing stats
    
    # Visualization settings
    show_labels=True,                      # Show element type labels
    box_width=3,                           # Bounding box thickness
    color_scheme="default"                 # Color scheme
)

# Create OCR config
ocr_config = OCRConfig(
    model_name="deepseek-ocr:3b",
    temperature=0.0,
    context_length=8192,
    use_grounding=True,
    output_config=custom_output
)

# Create OCR instance
ocr = OllamaOCR(config=ocr_config)
```

### 3.4 Configuration Flow Diagram

```
User Creates OllamaOCR
         │
         ▼
   Has config arg?
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    │         ▼
    │   Create default config
    │         │
    └────┬────┘
         │
         ▼
   Apply user parameters
   - model_name
   - output_dir
   - save_annotations
         │
         ▼
   Validate config
   - Check Ollama running
   - Check model exists
         │
         ▼
   Initialize components
   - OllamaExtractor
   - MultiPageProcessor
   - OutputManager
         │
         ▼
   Ready to process!
```

---

## 4. Processing Modes

### 4.1 Single File Processing

**Code:**
```python
from DocumentParser import OllamaOCR

ocr = OllamaOCR()
result = ocr.process("document.pdf")

print(f"Pages: {result.page_count}")
print(f"Elements: {result.get_total_elements()}")
print(f"Output: {result.output_dir}")
```

**Flow:**
```
User calls process()
         │
         ▼
Validate file exists
         │
         ▼
Create output directory
         │
         ▼
Detect file type
         │
    ┌────┴────┐
    │         │
   PDF      Image
    │         │
    ▼         │
Convert to    │
images        │
    │         │
    └────┬────┘
         │
         ▼
   [Image List]
         │
         ▼
FOR EACH image:
  ├─ Resize to 1024×1024
  ├─ Extract OCR
  ├─ Parse results
  ├─ Save outputs
  └─ Create annotations
         │
         ▼
Combine pages (if >1)
         │
         ▼
Generate metadata
         │
         ▼
Return DocumentResult
```

**Result Object:**
```python
result = ocr.process("doc.pdf")

# Access results
result.success           # bool: True/False
result.page_count        # int: Number of pages
result.page_results      # List[PageResult]: Per-page results
result.total_processing_time  # float: Seconds
result.output_dir        # str: Where files are saved

# Helper methods
result.get_total_elements()      # Total elements across all pages
result.get_successful_pages()    # Count of successful pages
result.get_failed_pages()        # List of failed page numbers
result.to_dict()                 # Convert to dictionary
```

---

### 4.2 Batch Processing

**Code:**
```python
from DocumentParser import OllamaOCR

ocr = OllamaOCR()

files = [
    "report_2024_Q1.pdf",
    "report_2024_Q2.pdf",
    "report_2024_Q3.pdf",
    "report_2024_Q4.pdf"
]

results = ocr.process_batch(files, verbose=True)

# Check results
for result in results:
    if result.success:
        print(f"✓ {result.input_file}: {result.page_count} pages")
    else:
        print(f"✗ {result.input_file}: {result.error_message}")
```

**Flow:**
```
User calls process_batch(files)
         │
         ▼
FOR EACH file in files:
  │
  ├─ Try: process(file)
  │   │
  │   ├─ Success? → Add result to list
  │   │
  │   └─ Error? → Create error result
  │
  └─ Continue to next file
         │
         ▼
Return list of results
```

**Parallel Processing (Future):**
```python
# Not yet implemented, but architecture supports it!

ocr = OllamaOCR()

results = ocr.process_batch(
    files,
    parallel=True,      # Process multiple files simultaneously
    max_workers=4       # Number of parallel workers
)
```

---

### 4.3 Page Range Processing

**Code:**
```python
ocr = OllamaOCR()

# Process only pages 1-5 of a PDF
result = ocr.process(
    "large_document.pdf",
    page_range=(1, 5)  # Only process first 5 pages
)
```

**Flow:**
```
process("doc.pdf", page_range=(1, 5))
         │
         ▼
Convert PDF to images
         │
         ▼
Filter images by page range
   [1, 2, 3, 4, 5]  # Only these
         │
         ▼
Process filtered pages
```

---

### 4.4 Custom Prompt Processing

**Code:**
```python
ocr = OllamaOCR()

# Use custom prompt for specific extraction
custom_prompt = "<image>\n<|grounding|>Extract only tables from this document."

result = ocr.process(
    "data_sheet.pdf",
    custom_prompt=custom_prompt
)
```

**Available Prompts (from DeepSeek documentation):**
```python
# Full document with grounding
"<image>\n<|grounding|>Convert the document to markdown."

# Simple OCR
"<image>\nFree OCR."

# Tables only
"<image>\n<|grounding|>Extract all tables."

# Parse figures
"<image>\nParse the figure."

# Detailed description
"<image>\nDescribe this image in detail."

# Locate specific text
"<image>\nLocate <|ref|>specific text<|/ref|> in the image."
```

---

## 5. Adding New Extractors

### 5.1 Extractor Architecture

All extractors must inherit from `BaseExtractor`:

```python
from DocumentParser.extractors import BaseExtractor, ExtractionResult

class MyCustomExtractor(BaseExtractor):
    """
    Custom extractor for a new model/backend.
    """
    
    def __init__(self, config):
        self.config = config
        # Initialize your model/client here
    
    def validate_config(self) -> bool:
        """Check if configuration is valid."""
        pass
    
    def is_available(self) -> bool:
        """Check if extractor is ready to use."""
        pass
    
    def extract(self, image_path: str, custom_prompt: Optional[str]) -> ExtractionResult:
        """Extract text and elements from image."""
        pass
```

### 5.2 Example: Adding Claude Vision Extractor

**Step 1: Create the extractor file**

**File:** `DocumentParser/extractors/claude_extractor.py`

```python
"""
Claude Vision Extractor
Uses Anthropic's Claude for OCR with vision capabilities.
"""

from pathlib import Path
from typing import Optional
import time
import base64

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ..config import OCRConfig
from ..parsers import parse_ocr_output
from .base_extractor import BaseExtractor, ExtractionResult


class ClaudeExtractor(BaseExtractor):
    """
    OCR extractor using Claude Vision.
    
    Example:
        >>> from DocumentParser.config import OCRConfig
        >>> config = OCRConfig(model_name="claude-3-5-sonnet-20241022")
        >>> extractor = ClaudeExtractor(config, api_key="your-key")
        >>> result = extractor.extract("document.png")
    """
    
    def __init__(self, config: OCRConfig, api_key: str):
        """
        Initialize Claude extractor.
        
        Args:
            config: OCR configuration
            api_key: Anthropic API key
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic library required. Install: pip install anthropic")
        
        self.config = config
        self.client = anthropic.Anthropic(api_key=api_key)
        
        print(f"✓ Claude extractor initialized")
        print(f"  Model: {config.model_name}")
    
    def validate_config(self) -> bool:
        """Validate configuration."""
        return self.client is not None
    
    def is_available(self) -> bool:
        """Check if extractor is ready."""
        return self.client is not None
    
    def extract(
        self,
        image_path: str,
        custom_prompt: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract text and elements from image using Claude.
        
        Args:
            image_path: Path to image file
            custom_prompt: Override default prompt
            
        Returns:
            ExtractionResult: Extraction results
        """
        start_time = time.time()
        
        # Validate image
        if not self.validate_image_path(image_path):
            return self.create_error_result(
                image_path=image_path,
                error_message=f"Invalid image path: {image_path}"
            )
        
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            # Determine media type
            suffix = Path(image_path).suffix.lower()
            media_type_map = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_type_map.get(suffix, 'image/png')
            
            # Get prompt
            if custom_prompt is None:
                custom_prompt = "Extract all text and elements from this document. Use markdown format."
            
            # Call Claude API
            message = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=8192,
                temperature=self.config.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": custom_prompt
                            }
                        ],
                    }
                ],
            )
            
            # Extract response
            raw_output = message.content[0].text if message.content else ""
            
            if not raw_output:
                return self.create_error_result(
                    image_path=image_path,
                    error_message="Empty response from Claude"
                )
            
            # Parse output
            parse_result = parse_ocr_output(raw_output)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create result
            return ExtractionResult(
                raw_output=raw_output,
                parse_result=parse_result,
                model_name=self.config.model_name,
                prompt_used=custom_prompt,
                image_path=image_path,
                processing_time=processing_time,
                success=True
            )
        
        except Exception as e:
            return self.create_error_result(
                image_path=image_path,
                error_message=f"Extraction failed: {str(e)}"
            )
    
    def get_info(self) -> dict:
        """Get extractor information."""
        return {
            'extractor_type': 'claude',
            'model_name': self.config.model_name,
            'backend': 'Anthropic API',
            'supports_grounding': False  # Claude doesn't have native grounding
        }
```

**Step 2: Update `extractors/__init__.py`**

```python
from .base_extractor import BaseExtractor, ExtractionResult
from .ollama_extractor import OllamaExtractor
from .multipage_processor import MultiPageProcessor, PageResult, DocumentResult

# Try to import optional extractors
try:
    from .claude_extractor import ClaudeExtractor
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

__all__ = [
    'BaseExtractor',
    'ExtractionResult',
    'OllamaExtractor',
    'MultiPageProcessor',
    'PageResult',
    'DocumentResult',
]

if CLAUDE_AVAILABLE:
    __all__.append('ClaudeExtractor')
```

**Step 3: Create new main class**

**File:** `DocumentParser/main.py` (add new class)

```python
class ClaudeOCR:
    """
    OCR system using Claude Vision.
    
    Example:
        >>> from DocumentParser import ClaudeOCR
        >>> ocr = ClaudeOCR(api_key="your-key")
        >>> result = ocr.process("document.pdf")
    """
    
    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        output_dir: str = "output"
    ):
        """
        Initialize ClaudeOCR.
        
        Args:
            model_name: Claude model to use
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            output_dir: Output directory
        """
        import os
        
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("API key required. Pass api_key or set ANTHROPIC_API_KEY")
        
        # Create config
        from .config import OCRConfig, get_full_output_config
        
        output_config = get_full_output_config()
        output_config.output_base_dir = output_dir
        
        self.config = OCRConfig(
            model_name=model_name,
            output_config=output_config
        )
        
        # Create extractor
        from .extractors import ClaudeExtractor
        self.extractor = ClaudeExtractor(self.config, api_key=api_key)
        
        # Create processor
        from .extractors import MultiPageProcessor
        self.processor = MultiPageProcessor(
            extractor=self.extractor,
            output_config=output_config
        )
    
    def process(self, file_path: str, **kwargs):
        """Process a document."""
        return self.processor.process_document(file_path, **kwargs)
```

**Step 4: Update package `__init__.py`**

```python
# DocumentParser/__init__.py

from .main import OllamaOCR, create_ocr

# Try to import optional OCR classes
try:
    from .main import ClaudeOCR
    __all__ = ['OllamaOCR', 'ClaudeOCR', 'create_ocr']
except ImportError:
    __all__ = ['OllamaOCR', 'create_ocr']
```

**Step 5: Usage**

```python
from DocumentParser import ClaudeOCR

# Create OCR instance
ocr = ClaudeOCR(
    model_name="claude-3-5-sonnet-20241022",
    api_key="your-api-key",
    output_dir="my_output"
)

# Process document
result = ocr.process("document.pdf")

print(f"Pages: {result.page_count}")
print(f"Output: {result.output_dir}")
```

### 5.3 Extractor Flow Diagram

```
New Extractor Integration
         │
         ▼
1. Create extractor class
   (inherit BaseExtractor)
         │
         ▼
2. Implement required methods:
   - validate_config()
   - is_available()
   - extract()
         │
         ▼
3. Add to extractors/__init__.py
         │
         ▼
4. Create main class (optional)
   - MyModelOCR
         │
         ▼
5. Add to package __init__.py
         │
         ▼
6. Document usage
         │
         ▼
   Ready to use!
```

---

## 6. Adding New Models

### 6.1 Model Registry System

**File:** `DocumentParser/config/model_registry.py`

```python
# Existing models
SUPPORTED_MODELS = {
    "deepseek-ocr:3b": {
        "name": "DeepSeek OCR 3B",
        "supports_grounding": True,
        "recommended_resolution": 1024,
        "context_length": 8192,
    },
    "llava:13b": {
        "name": "LLaVA 13B",
        "supports_grounding": False,
        "recommended_resolution": 640,
        "context_length": 4096,
    },
}
```

### 6.2 Adding a New Model

**Scenario:** You want to add support for `qwen-vl:7b`

**Step 1: Add to model registry**

```python
# DocumentParser/config/model_registry.py

SUPPORTED_MODELS = {
    # ... existing models ...
    
    "qwen-vl:7b": {
        "name": "Qwen-VL 7B",
        "supports_grounding": True,      # Does it support bounding boxes?
        "recommended_resolution": 1024,  # Optimal image size
        "context_length": 8192,          # Max tokens
        "temperature": 0.0,              # Recommended temperature
        "description": "Alibaba's vision-language model with strong OCR capabilities"
    },
}
```

**Step 2: Create custom prompt (if needed)**

```python
# DocumentParser/config/prompts.py

def get_qwen_ocr_prompt() -> str:
    """
    Prompt optimized for Qwen-VL.
    """
    return "<img></img>\nExtract all text and structure from this document."

# Add to get_prompt_for_model()
def get_prompt_for_model(model_name: str, use_grounding: bool = True) -> str:
    if "qwen" in model_name.lower():
        return get_qwen_ocr_prompt()
    elif "deepseek" in model_name.lower():
        return get_deepseek_ocr_prompt(use_grounding)
    # ... etc
```

**Step 3: Test the model**

```python
from DocumentParser import OllamaOCR

# First, pull the model
# $ ollama pull qwen-vl:7b

# Use the new model
ocr = OllamaOCR(model_name="qwen-vl:7b")
result = ocr.process("test_document.pdf")

print(f"Model: {result.page_results[0].extraction_result.model_name}")
print(f"Success: {result.success}")
```

**Step 4: Document model-specific quirks**

```python
# Add to model registry
"qwen-vl:7b": {
    "name": "Qwen-VL 7B",
    "supports_grounding": True,
    "recommended_resolution": 1024,
    "context_length": 8192,
    
    # Model-specific notes
    "notes": {
        "strengths": ["Chinese text", "Complex layouts", "Fast inference"],
        "limitations": ["Less accurate on handwriting", "Requires more RAM"],
        "optimal_use_cases": ["Asian language documents", "Technical diagrams"]
    }
}
```

### 6.3 Model Comparison Table

| Model | Grounding | Resolution | Speed | Accuracy | Best For |
|-------|-----------|------------|-------|----------|----------|
| deepseek-ocr:3b | ✅ Yes | 1024×1024 | Fast | High | General documents |
| llava:13b | ❌ No | 640×640 | Medium | Medium | Simple OCR |
| qwen-vl:7b | ✅ Yes | 1024×1024 | Fast | High | Asian languages |
| claude-3.5 | ❌ No | Dynamic | Slow | Very High | Complex analysis |

### 6.4 Prompt Templates for Different Models

```python
# DocumentParser/config/prompts.py

PROMPT_TEMPLATES = {
    "deepseek": {
        "grounding": "<image>\n<|grounding|>Convert the document to markdown.",
        "simple": "<image>\nFree OCR.",
        "tables": "<image>\n<|grounding|>Extract all tables.",
    },
    
    "llava": {
        "default": "Extract all text from this image in markdown format.",
        "detailed": "Describe this document in detail, including all text and layout.",
    },
    
    "qwen": {
        "default": "<img></img>\nExtract all text and structure.",
        "chinese": "<img></img>\n提取文档中的所有文本和结构。",
    },
    
    "claude": {
        "default": "Extract all text and elements from this document. Use markdown format.",
        "structured": "Analyze this document and extract:\n1. All text content\n2. Tables\n3. Image descriptions\n4. Document structure",
    }
}
```

---

## 7. Module Deep Dive

### 7.1 Config Module

**Purpose:** Centralized configuration management

**Key Files:**
- `model_config.py` - OCRConfig class
- `output_config.py` - OutputConfig class
- `model_registry.py` - Supported models
- `prompts.py` - Prompt templates

**Example Config Creation:**

```python
from DocumentParser.config import OCRConfig, OutputConfig

# Create output config
output_config = OutputConfig(
    output_base_dir="results",
    save_per_page={'raw_output': True, 'grounding_json': True},
    create_combined=True
)

# Create OCR config
ocr_config = OCRConfig(
    model_name="deepseek-ocr:3b",
    temperature=0.0,
    output_config=output_config
)

# Validate
ocr_config.validate()  # Raises exception if invalid
```

### 7.2 Parsers Module

**Purpose:** Convert raw model output to structured data

**Parser Types:**

1. **GroundingParser** - Parses `<|ref|><|det|>` format
2. **MarkdownParser** - Parses plain markdown
3. **Parser Registry** - Auto-detects format

**Example Raw Output → Parsed:**

```python
# Raw output from model
raw = """
<|ref|>title<|/ref|><|det|>[[100,50,500,100]]<|/det|>
Data Collection: Tables

<|ref|>text<|/ref|><|det|>[[50,150,700,200]]<|/det|>
Each table should have a caption.
"""

# Parse
from DocumentParser.parsers import parse_ocr_output

result = parse_ocr_output(raw)

# Access parsed elements
for element in result.elements:
    print(f"{element.element_type}: {element.bbox}")
    print(f"Content: {element.content[:50]}...")
```

**Output:**
```
title: [100, 50, 500, 100]
Content: Data Collection: Tables...

text: [50, 150, 700, 200]
Content: Each table should have a caption....
```

### 7.3 Processors Module

**Purpose:** File format conversions and preprocessing

**Key Classes:**

#### **PDFProcessor**
Converts PDF to images using PyMuPDF or pdf2image.

```python
from DocumentParser.processors import PDFProcessor

processor = PDFProcessor(dpi=300)

# Convert PDF to images
images = processor.convert_pdf(
    pdf_path="document.pdf",
    output_dir="temp_pages"
)

# Returns: ['temp_pages/page_001.png', 'temp_pages/page_002.png', ...]
```

#### **ImageProcessor**
Image preprocessing (resize, normalize, etc.)

```python
from DocumentParser.processors import ImageProcessor

processor = ImageProcessor()

# Resize for OCR
resized = processor.resize_for_ocr(
    image_path="large_image.png",
    target_size=1024
)
```

### 7.4 Extractors Module

**Purpose:** Interface with OCR models

**Key Components:**

#### **BaseExtractor** (Abstract)
Defines interface all extractors must implement.

#### **OllamaExtractor**
Communicates with Ollama models.

```python
from DocumentParser.extractors import OllamaExtractor
from DocumentParser.config import OCRConfig

config = OCRConfig(model_name="deepseek-ocr:3b")
extractor = OllamaExtractor(config)

# Extract from single image
result = extractor.extract("document.png")

# Access results
print(result.raw_output)           # Raw model response
print(result.parse_result.elements) # Parsed elements
print(result.processing_time)      # Seconds
```

#### **MultiPageProcessor**
Orchestrates multi-page document processing.

```python
from DocumentParser.extractors import MultiPageProcessor, OllamaExtractor

extractor = OllamaExtractor(config)
processor = MultiPageProcessor(extractor, output_config)

# Process entire document
result = processor.process_document("report.pdf")

# Access per-page results
for page_result in result.page_results:
    print(f"Page {page_result.page_number}: {page_result.extraction_result.get_element_count()} elements")
```

### 7.5 Visualizers Module

**Purpose:** Create annotated images

```python
from DocumentParser.visualizers import BBoxVisualizer

visualizer = BBoxVisualizer(
    show_labels=True,
    show_ids=True,
    box_width=3,
    color_scheme="default"
)

# Create annotated image
visualizer.visualize(
    image_path="document.png",
    elements=parsed_elements,
    output_path="annotated.png"
)

# Create side-by-side comparison
visualizer.create_comparison(
    original_path="document.png",
    annotated_path="annotated.png",
    output_path="comparison.png"
)
```

### 7.6 Storage Module

**Purpose:** Manage output files and directories

#### **DirectoryBuilder**
Creates organized folder structure.

```python
from DocumentParser.storage import DirectoryBuilder
from DocumentParser.config import OutputConfig

builder = DirectoryBuilder(output_config)

# Create document structure
doc_dir = builder.create_document_structure("report.pdf")
# Creates: output/report/

# Create page directory
page_dir = builder.create_page_directory(doc_dir, page_number=1)
# Creates: output/report/pages/page_001/
```

#### **OutputManager**
Saves extraction results.

```python
from DocumentParser.storage import OutputManager

manager = OutputManager(output_config)

# Save page results
manager.save_page_result(
    result=extraction_result,
    page_number=1,
    page_dir="output/report/pages/page_001"
)

# Saves:
# - raw_output.txt
# - grounding.json
# - page_001.md (if enabled)
```

---

## 8. Extension Points

### 8.1 Custom Parsers

**When to create:** New model outputs in different format

```python
from DocumentParser.parsers import BaseParser, ParseResult

class CustomParser(BaseParser):
    """Parse custom format."""
    
    def parse(self, raw_text: str) -> ParseResult:
        # Your parsing logic
        elements = []
        # ... parse raw_text ...
        
        return ParseResult(
            elements=elements,
            raw_text=raw_text,
            parser_type="custom",
            success=True
        )
    
    def can_parse(self, text: str) -> bool:
        """Detect if this parser can handle the text."""
        return "YOUR_FORMAT_INDICATOR" in text
```

**Register parser:**
```python
# In parsers/parser_registry.py
from .custom_parser import CustomParser

PARSER_REGISTRY = [
    GroundingParser(),
    CustomParser(),      # Add your parser
    MarkdownParser(),    # Fallback
]
```

### 8.2 Custom Processors

**When to create:** New file formats or preprocessing

```python
from PIL import Image

class DocxProcessor:
    """Convert DOCX to images."""
    
    def convert_docx(self, docx_path: str, output_dir: str) -> list:
        """Convert DOCX pages to images."""
        # Use python-docx or other library
        # Return list of image paths
        pass
```

**Integrate into pipeline:**
```python
# In multipage_processor.py
def _process_document(self, file_path):
    if file_path.endswith('.docx'):
        images = self.docx_processor.convert_docx(file_path)
    elif file_path.endswith('.pdf'):
        images = self.pdf_processor.convert_pdf(file_path)
    # ...
```

### 8.3 Custom Visualizers

**When to create:** Different visualization styles

```python
from DocumentParser.visualizers import BBoxVisualizer

class HeatmapVisualizer:
    """Show element density as heatmap."""
    
    def create_heatmap(self, elements, image_path, output_path):
        # Create density heatmap from bboxes
        pass
```

### 8.4 Post-Processing Hooks

**Add custom processing after extraction:**

```python
class CustomOCR(OllamaOCR):
    """OCR with custom post-processing."""
    
    def process(self, file_path, **kwargs):
        # Run normal processing
        result = super().process(file_path, **kwargs)
        
        # Add custom post-processing
        result = self._post_process(result)
        
        return result
    
    def _post_process(self, result):
        """Custom post-processing."""
        # Example: Filter elements
        for page_result in result.page_results:
            elements = page_result.extraction_result.get_elements()
            # Filter out elements with confidence < 0.5
            filtered = [e for e in elements if e.confidence > 0.5]
            # Update result...
        
        return result
```

---

## 9. Troubleshooting Guide

### 9.1 Common Issues

#### **Issue: Bounding boxes misaligned**

**Cause:** Image size mismatch between processing and annotation

**Solution:**
```python
# Ensure consistent image size
# In multipage_processor.py, always use resized_path:

extraction_result = self.extractor.extract(
    image_path=str(resized_path),  # ← Must be resized!
    ...
)

self._create_page_annotation(
    image_path=str(resized_path),  # ← Same image!
    ...
)
```

#### **Issue: Empty extraction results**

**Cause:** Prompt not suitable for model, or image quality

**Debug:**
```python
# Check raw output
result = extractor.extract("image.png")
print(result.raw_output)  # See what model returned

# Try different prompt
result = extractor.extract(
    "image.png",
    custom_prompt="<image>\nFree OCR."  # Simpler prompt
)
```

#### **Issue: Ollama connection failed**

**Cause:** Ollama not running

**Solution:**
```bash
# Start Ollama
ollama serve

# Check if model exists
ollama list

# Pull model if needed
ollama pull deepseek-ocr:3b
```

#### **Issue: Out of memory**

**Cause:** Processing very large images or PDFs

**Solution:**
```python
# Reduce image size
config = OCRConfig(...)
processor = MultiPageProcessor(extractor, config)

# OR process in smaller batches
for i in range(0, len(files), 10):
    batch = files[i:i+10]
    results = ocr.process_batch(batch)
```

### 9.2 Debug Mode

**Enable verbose logging:**

```python
# Set verbose mode
ocr = OllamaOCR()

result = ocr.process(
    "document.pdf",
    verbose=True  # Shows detailed progress
)
```

**Check intermediate files:**
```bash
# Temp pages (before processing)
output/document/temp_pages/
├── page_001.png        # Original size
└── page_001_ocr.png    # Resized for OCR

# Per-page outputs
output/document/pages/page_001/
├── raw_output.txt      # Check raw model response
├── grounding.json      # Check parsed elements
└── page_001.md         # Check markdown output
```

### 9.3 Performance Optimization

**Slow processing:**

1. **Use smaller model:** `deepseek-ocr:3b` faster than `:7b`
2. **Reduce image size:** 640×640 instead of 1024×1024
3. **Disable visualizations:** Set `save_annotations=False`
4. **Process specific pages:** Use `page_range=(1, 10)`

**Memory optimization:**

```python
# Process one page at a time (future feature)
for page in range(1, total_pages + 1):
    result = ocr.process(
        "large_doc.pdf",
        page_range=(page, page)
    )
    # Process result immediately
    # Free memory before next page
```

---

## 10. Best Practices

### 10.1 Production Deployment

**Use explicit configuration:**
```python
# DON'T (implicit defaults)
ocr = OllamaOCR()

# DO (explicit configuration)
config = OCRConfig(
    model_name="deepseek-ocr:3b",
    temperature=0.0,
    context_length=8192,
    output_config=get_full_output_config()
)
ocr = OllamaOCR(config=config)
```

**Handle errors gracefully:**
```python
try:
    result = ocr.process("document.pdf")
    
    if not result.success:
        logger.error(f"Processing failed: {result.error_message}")
        # Send alert, retry, etc.
    
    # Check for partial failures
    failed_pages = result.get_failed_pages()
    if failed_pages:
        logger.warning(f"Failed pages: {failed_pages}")

except Exception as e:
    logger.exception("Unexpected error")
    # Fallback handling
```

**Log processing stats:**
```python
result = ocr.process("document.pdf")

logger.info(f"Processed {result.input_file}")
logger.info(f"  Pages: {result.page_count}")
logger.info(f"  Elements: {result.get_total_elements()}")
logger.info(f"  Time: {result.total_processing_time:.2f}s")
logger.info(f"  Output: {result.output_dir}")
```

### 10.2 Testing

**Unit test structure:**
```python
import pytest
from DocumentParser import OllamaOCR

def test_single_page_processing():
    ocr = OllamaOCR()
    result = ocr.process("test_data/single_page.pdf")
    
    assert result.success
    assert result.page_count == 1
    assert result.get_total_elements() > 0

def test_multi_page_processing():
    ocr = OllamaOCR()
    result = ocr.process("test_data/multi_page.pdf")
    
    assert result.success
    assert result.page_count > 1
    assert len(result.page_results) == result.page_count

def test_custom_prompt():
    ocr = OllamaOCR()
    custom_prompt = "<image>\nExtract tables only."
    
    result = ocr.process(
        "test_data/table_doc.pdf",
        custom_prompt=custom_prompt
    )
    
    assert result.success
    # Check that results contain tables
```

### 10.3 Code Organization

**Good:**
```python
# main_processing.py
from DocumentParser import OllamaOCR
from DocumentParser.config import get_full_output_config

class DocumentProcessor:
    def __init__(self, model_name="deepseek-ocr:3b"):
        config = get_full_output_config()
        self.ocr = OllamaOCR(model_name=model_name, config=config)
    
    def process_document(self, file_path):
        return self.ocr.process(file_path)
    
    def process_batch(self, files):
        return self.ocr.process_batch(files)

# Usage
processor = DocumentProcessor()
result = processor.process_document("doc.pdf")
```

**Bad:**
```python
# Everything in one file
import ollama
from PIL import Image
# ... 500 lines of code ...

def process_pdf(file):
    # Direct model calls
    # No error handling
    # Hard to test
    pass
```

### 10.4 Documentation

**Document your configuration:**
```python
# config.py
"""
OCR Configuration for Production

This configuration is optimized for:
- High accuracy
- Japanese manufacturing documents
- Batch processing
"""

from DocumentParser.config import OCRConfig, OutputConfig

def get_production_config():
    output_config = OutputConfig(
        output_base_dir="production_output",
        save_per_page={
            'raw_output': True,
            'grounding_json': True,
            'annotated_image': True,  # For QA review
        },
        create_combined=True,
        save_metadata=True
    )
    
    return OCRConfig(
        model_name="deepseek-ocr:3b",
        temperature=0.0,  # Deterministic
        context_length=8192,  # Handle long documents
        output_config=output_config
    )
```

---

## Quick Reference

### Common Commands

```python
# Basic usage
from DocumentParser import OllamaOCR
ocr = OllamaOCR()
result = ocr.process("document.pdf")

# Custom configuration
from DocumentParser.config import get_full_output_config, OCRConfig
config = OCRConfig(output_config=get_full_output_config())
ocr = OllamaOCR(config=config)

# Batch processing
results = ocr.process_batch(["doc1.pdf", "doc2.pdf"])

# Custom prompt
result = ocr.process("doc.pdf", custom_prompt="Extract tables only")

# Page range
result = ocr.process("doc.pdf", page_range=(1, 5))
```

### Configuration Presets

```python
from DocumentParser.config import (
    get_default_output_config,  # Basic
    get_full_output_config,     # Everything
    get_minimal_output_config,  # Raw text only
    get_fast_config,            # Speed optimized
    get_quality_config          # Accuracy optimized
)
```

### Result Access

```python
result = ocr.process("doc.pdf")

# Basic info
result.success                    # bool
result.page_count                 # int
result.output_dir                 # str
result.total_processing_time      # float

# Helper methods
result.get_total_elements()       # int
result.get_successful_pages()     # int
result.get_failed_pages()         # List[int]
result.to_dict()                  # dict

# Per-page access
for page in result.page_results:
    page.page_number              # int
    page.extraction_result        # ExtractionResult
    page.extraction_result.get_elements()  # List[ParsedElement]
```

---

**End of Documentation**

This comprehensive guide covers everything needed to understand, use, extend, and maintain the DocumentParser system. For questions or contributions, refer to the project repository.