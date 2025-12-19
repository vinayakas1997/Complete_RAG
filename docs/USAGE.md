# DocumentParser Usage Guide

## 1. Installation

Ensure you have the required dependencies and Ollama installed.

### Prerequisites
- **Ollama**: Must be installed and running (`ollama serve`).
- **Python**: 3.8+

### Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install ollama Pillow pymupdf pdf2image
   ```
3. Pull the recommended model:
   ```bash
   ollama pull deepseek-ocr:3b
   ```

## 2. Basic Usage

The primary interface is the `OllamaOCR` class in `main.py`.

### Simple Document Processing

```python
from main import OllamaOCR

# Initialize with default settings
ocr = OllamaOCR()

# Process a file (PDF or Image)
# This will:
# 1. Provide status in the console
# 2. Save results to the 'output' directory
result = ocr.process("path/to/document.pdf")

if result.success:
    print("Success!")
else:
    print(f"Error: {result.error_message}")
```

### Specifying a Model

```python
# Use a specific model
ocr = OllamaOCR(model_name="llava:13b")

# Or use convenience function
from main import create_ocr
ocr = create_ocr("qwen-vl:7b")
```

## 3. Advanced Configuration

You can customize the behavior using `OCRConfig`.

```python
from main import OllamaOCR
from config import OCRConfig, create_quality_config

# Option 1: Pass arguments directly to constructor
ocr = OllamaOCR(
    model_name="deepseek-ocr:3b",
    use_grounding=True,       # Enable/disable bounding boxes
    output_dir="./results",   # Custom output directory
    save_annotations=True,    # Save images with drawn boxes
    quality_mode=True         # Optimize for quality (slower)
)

# Option 2: Full configuration object
config = create_quality_config()
config.model_name = "deepseek-ocr:3b"
config.output_config.save_json = True
config.output_config.save_markdown = True

ocr = OllamaOCR(config=config)
```

## 4. Batch Processing

Process multiple files efficiently.

```python
files = [
    "invoices/inv_001.pdf",
    "invoices/inv_002.pdf",
    "scans/image_001.png"
]

ocr = OllamaOCR()
results = ocr.process_batch(files)

for res in results:
    print(f"{res.input_file}: {res.page_count} pages processed.")
```

## 5. Output formats

The system generates a structured output directory for each document:

```text
output/
└── document_name/
    ├── page_001/
    │   ├── raw_output.txt          # Raw text from model
    │   ├── elements.json           # Structured data with coords
    │   ├── page_001_annotated.png  # Image with bounding boxes
    │   └── page_001_comparison.png # Side-by-side view
    ├── page_002/
    └── combined/
        ├── full_document.md        # Combined markdown
        └── full_document.json      # Combined JSON
```

### JSON Structure (`elements.json`)
```json
{
  "elements": [
    {
      "id": 1,
      "label": "header",
      "box": [100, 50, 500, 100],  # [x1, y1, x2, y2]
      "content": "Invoice #12345",
      "confidence": 0.95
    }
  ]
}
```
