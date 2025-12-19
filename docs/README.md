# DocumentParser System Documentation

## Overview

**DocumentParser** is a production-grade, local OCR system powered by Ollama's vision models (like DeepSeek-OCR, LLaVA, Llama-Vision). It is designed to extract text, structured tables, and bounding box groundings from PDFs and images with high accuracy.

### Key Features
- **Local Privacy**: Runs entirely on your machine using Ollama.
- **Multi-Model Support**: Compatible with DeepSeek-OCR, LLaVA, Qwen-VL, and more.
- **Intelligent Extraction**:
  - Full text extraction.
  - Structural understanding (tables, headers).
  - **Grounding**: Returns bounding boxes for detected elements.
- **Robust Processing**:
  - Multi-page PDF orchestration.
  - Automatic error handling and retry logic.
  - Image preprocessing (auto-resizing for optimal model performance).
- **Rich Output**:
  - Markdown, JSON, and raw text formats.
  - Visual annotations (bounding boxes drawn on images).
  - Side-by-side comparison views.

## Documentation Index

This documentation suite is organized as follows:

| Document | Description |
|----------|-------------|
| **[Usage Guide](USAGE.md)** | **Start Here.** How to install, configure, and use the Python API. Includes code examples for common scenarios. |
| **[Architecture](ARCHITECTURE.md)** | Deep dive into the system design, detailed flow graphs (Mermaid), and component interaction diagrams. |

## Quick Start

```python
from main import OllamaOCR

# Initialize
ocr = OllamaOCR(model_name="deepseek-ocr:3b")

# Process a document
result = ocr.process("documents/invoice.pdf")

print(f"Processed {result.page_count} pages.")
print(f"Output saved to: {result.output_dir}")
```
