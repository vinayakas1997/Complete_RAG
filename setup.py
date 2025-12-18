"""
Setup configuration for DeepSeek OCR package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="deepseek-ocr",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Complete OCR system for Ollama-based vision models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deepseek-ocr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ollama>=0.4.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "PyMuPDF>=1.23.0",
        "pdf2image>=1.16.3",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "deepseek-ocr=deepseek_ocr.cli:main",  # Optional CLI
        ],
    },
)
# ```

# ---

# ## Final Directory Structure:
# ```
# deepseek_ocr_project/
# │
# ├── deepseek_ocr/                    ← THE PACKAGE
# │   ├── __init__.py                  ← Exports OllamaOCR
# │   ├── main.py                      ← Main OCR class
# │   │
# │   ├── utils/
# │   │   ├── __init__.py
# │   │   ├── file_utils.py
# │   │   └── network_utils.py
# │   │
# │   ├── config/
# │   │   ├── __init__.py
# │   │   ├── model_registry.py
# │   │   ├── prompts.py
# │   │   ├── output_config.py
# │   │   └── model_config.py
# │   │
# │   ├── parsers/
# │   │   ├── __init__.py
# │   │   ├── base_parser.py
# │   │   ├── grounding_parser.py
# │   │   ├── markdown_parser.py
# │   │   └── parser_registry.py
# │   │
# │   ├── processors/
# │   │   ├── __init__.py
# │   │   ├── pdf_processor.py
# │   │   └── image_processor.py
# │   │
# │   ├── extractors/
# │   │   ├── __init__.py
# │   │   ├── base_extractor.py
# │   │   ├── ollama_extractor.py
# │   │   └── multipage_processor.py
# │   │
# │   ├── visualizers/
# │   │   ├── __init__.py
# │   │   └── bbox_visualizer.py
# │   │
# │   └── storage/
# │       ├── __init__.py
# │       ├── directory_builder.py
# │       └── output_manager.py
# │
# ├── tests/
# │   ├── __init__.py
# │   └── test_system.py
# │
# ├── examples/
# │   ├── basic_usage.py
# │   ├── batch_processing.py
# │   └── custom_config.py
# │
# ├── setup.py                         ← For pip install
# ├── requirements.txt                 ← Dependencies
# ├── README.md                        ← Documentation
# ├── LICENSE                          ← License file
# └── .gitignore                       ← Git ignore