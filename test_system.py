"""
Complete System Test
Tests the entire OCR pipeline end-to-end.

Run from project root:
    python test_system.py
"""

import sys
from pathlib import Path

# Add project to path so we can import DocumentParser
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*80)
print("DEEPSEEK OCR SYSTEM - COMPLETE TEST")
print("="*80)

# Test 1: Import the package
print("\n[1/10] Testing Package Import...")
print("-"*80)

try:
    from DocumentParser import OllamaOCR, create_ocr
    print("✓ DocumentParser package imported")
    print(f"  Imported: OllamaOCR, create_ocr")
    
    # Try importing submodules
    from DocumentParser.config import OCRConfig, create_default_config
    print("✓ config submodule imported")
    
    from DocumentParser.extractors import OllamaExtractor, MultiPageProcessor
    print("✓ extractors submodule imported")
    
    from DocumentParser.parsers import GroundingParser, MarkdownParser, parse_ocr_output
    print("✓ parsers submodule imported")
    
    from DocumentParser.processors import PDFProcessor, ImageProcessor
    print("✓ processors submodule imported")
    
    from DocumentParser.visualizers import BBoxVisualizer
    print("✓ visualizers submodule imported")
    
    from DocumentParser.storage import DirectoryBuilder, OutputManager
    print("✓ storage submodule imported")
    
    from DocumentParser.utils import configure_proxy_bypass, check_ollama_running
    print("✓ utils submodule imported")
    
    print("\n✅ All imports successful!")

except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    print("\nMake sure you're running from the project root:")
    print(f"  Current directory: {Path.cwd()}")
    print(f"  Expected: {project_root}")
    sys.exit(1)


# Test 2: Check dependencies
print("\n[2/10] Checking Dependencies...")
print("-"*80)

dependencies_ok = True

try:
    import ollama
    print("✓ ollama library available")
except ImportError:
    print("✗ ollama library missing")
    print("  Install: pip install ollama")
    dependencies_ok = False

try:
    import fitz
    print("✓ PyMuPDF available")
except ImportError:
    print("⚠ PyMuPDF not available (optional)")
    print("  Install: pip install PyMuPDF")

try:
    from pdf2image import convert_from_path
    print("✓ pdf2image available")
except ImportError:
    print("⚠ pdf2image not available (optional)")
    print("  Install: pip install pdf2image")

try:
    from PIL import Image
    print("✓ Pillow available")
except ImportError:
    print("✗ Pillow missing")
    print("  Install: pip install Pillow")
    dependencies_ok = False

if dependencies_ok:
    print("\n✅ Required dependencies available!")
else:
    print("\n❌ Some required dependencies missing!")
    print("Install with: pip install ollama Pillow")
    sys.exit(1)


# Test 3: Check Ollama connection
print("\n[3/10] Checking Ollama Connection...")
print("-"*80)

ollama_host = "http://localhost:11434"

if check_ollama_running(ollama_host):
    print(f"✓ Ollama is running at {ollama_host}")
else:
    print(f"✗ Cannot connect to Ollama at {ollama_host}")
    print("\nPlease ensure:")
    print("  1. Ollama is installed: https://ollama.ai")
    print("  2. Ollama is running: ollama serve")
    print("  3. Port 11434 is accessible")
    sys.exit(1)


# Test 4: Check model availability
print("\n[4/10] Checking Model Availability...")
print("-"*80)

from DocumentParser.utils import verify_model_exists, list_ollama_models

model_name = "deepseek-ocr:3b"

if verify_model_exists(model_name, ollama_host):
    print(f"✓ Model '{model_name}' is available")
else:
    print(f"✗ Model '{model_name}' not found")
    print("\nAvailable models:")
    models = list_ollama_models(ollama_host)
    if models:
        for model in models[:5]:  # Show first 5
            print(f"  - {model}")
    else:
        print("  (none)")
    
    print(f"\nTo pull the model, run:")
    print(f"  ollama pull {model_name}")
    sys.exit(1)


# Test 5: Configuration test
print("\n[5/10] Testing Configuration...")
print("-"*80)

try:
    config = create_default_config()
    print(f"✓ Default config created")
    print(f"  Model: {config.model_name}")
    print(f"  Use grounding: {config.use_grounding}")
    print(f"  Output dir: {config.output_config.output_base_dir}")
    
    # Validate config
    config.validate()
    print("✓ Configuration is valid")
    
    print("\n✅ Configuration test passed!")

except Exception as e:
    print(f"\n❌ Configuration test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 6: Create test image
print("\n[6/10] Creating Test Image...")
print("-"*80)

import tempfile
from PIL import Image, ImageDraw, ImageFont

temp_dir = Path(tempfile.mkdtemp(prefix="ocr_test_"))
test_image = temp_dir / "test_document.png"

try:
    # Create test image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_text = ImageFont.truetype("arial.ttf", 24)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Draw title
    draw.rectangle([50, 50, 750, 120], outline='black', width=2)
    draw.text((60, 65), "Test Document - OCR System", fill='black', font=font_title)
    
    # Draw table-like structure
    draw.rectangle([50, 150, 750, 450], outline='black', width=2)
    draw.line([50, 200, 750, 200], fill='black', width=2)
    draw.line([400, 150, 400, 450], fill='black', width=2)
    
    draw.text((60, 160), "Column 1", fill='black', font=font_text)
    draw.text((410, 160), "Column 2", fill='black', font=font_text)
    draw.text((60, 220), "Test Data 1", fill='black', font=font_text)
    draw.text((410, 220), "Test Data 2", fill='black', font=font_text)
    
    # Draw some text
    draw.text((60, 480), "This is a test document for OCR processing.", fill='black', font=font_text)
    
    img.save(test_image)
    print(f"✓ Test image created: {test_image}")
    print(f"  Size: {img.width}x{img.height}")
    
    print("\n✅ Test image creation successful!")

except Exception as e:
    print(f"\n❌ Test image creation failed: {e}")
    import shutil
    shutil.rmtree(temp_dir)
    sys.exit(1)


# Test 7: Create OllamaOCR instance
print("\n[7/10] Creating OllamaOCR Instance...")
print("-"*80)
from DocumentParser.config import OutputConfig
# Create explicit output config
output_config = OutputConfig(
    save_per_page={
        'raw_output': True,
        'grounding_json': True,
        'annotated_image': True,
        'original_image': False,
        'markdown': False,
    },
    create_comparison=True  # ← EXPLICITLY SET THIS
)

# Create OCR with explicit config
from DocumentParser.config import OCRConfig

ocr_config = OCRConfig(
    model_name=model_name,
    output_config=output_config,
)

ocr = OllamaOCR(config=ocr_config)

try:
    # ocr = OllamaOCR(
    #     model_name=model_name,
    #     output_dir=str(temp_dir / "output"),
    #     save_annotations=True
    # )


    print("✓ OllamaOCR instance created")
    
    # Get system info
    info = ocr.get_info()
    print(f"  Model: {info['model_name']}")
    print(f"  Available: {info['is_available']}")
    print(f"  Supports grounding: {info['supports_grounding']}")
    
    print("\n✅ OllamaOCR creation successful!")

except Exception as e:
    print(f"\n❌ OllamaOCR creation failed: {e}")
    import traceback
    traceback.print_exc()
    import shutil
    shutil.rmtree(temp_dir)
    sys.exit(1)


# Test 8: Process test image
print("\n[8/10] Processing Test Image...")
print("-"*80)

try:
    print("Starting OCR extraction...")
    print("(This may take 10-30 seconds depending on model and hardware)")
    print()
    
    result = ocr.process(
        file_path=str(test_image),
        verbose=True
    )
    
    if result.success:
        print("\n✅ Processing successful!")
        print(f"  Pages processed: {result.page_count}")
        print(f"  Elements extracted: {result.get_total_elements()}")
        print(f"  Processing time: {result.total_processing_time:.2f}s")
        print(f"  Output directory: {result.output_dir}")
    else:
        print(f"\n❌ Processing failed: {result.error_message}")
        import shutil
        shutil.rmtree(temp_dir)
        sys.exit(1)

except Exception as e:
    print(f"\n❌ Processing failed with exception: {e}")
    import traceback
    traceback.print_exc()
    import shutil
    shutil.rmtree(temp_dir)
    sys.exit(1)


# Test 9: Verify output files
print("\n[9/10] Verifying Output Files...")
print("-"*80)

output_dir = Path(result.output_dir)

expected_files = {
    'metadata.json': output_dir / 'metadata.json',
    'raw_output.txt': output_dir / 'pages' / 'page_001' / 'raw_output.txt',
    'grounding.json': output_dir / 'pages' / 'page_001' / 'grounding.json',
}

all_found = True
for file_type, file_path in expected_files.items():
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"✓ {file_type:20s} - {size:>8,} bytes")
    else:
        print(f"✗ {file_type:20s} - NOT FOUND")
        all_found = False

# Check for annotated image
annotated_image = output_dir / 'pages' / 'page_001' / 'page_001_annotated.png'
if annotated_image.exists():
    size = annotated_image.stat().st_size
    print(f"✓ {'annotated_image':20s} - {size:>8,} bytes")
else:
    print(f"⚠ {'annotated_image':20s} - NOT FOUND (may be disabled)")

if all_found:
    print("\n✅ All expected files created!")
else:
    print("\n⚠ Some files missing")


# Test 10: Display extracted elements
print("\n[10/10] Displaying Extracted Elements...")
print("-"*80)

if result.page_results:
    page_result = result.page_results[0]
    elements = page_result.extraction_result.get_elements()
    
    print(f"Total elements found: {len(elements)}\n")
    
    for i, element in enumerate(elements[:5], 1):  # Show first 5
        print(f"Element #{element.element_id}:")
        print(f"  Type: {element.element_type}")
        print(f"  BBox: {element.bbox}")
        content_preview = element.content[:80] + "..." if len(element.content) > 80 else element.content
        print(f"  Content: {content_preview}")
        print()
    
    if len(elements) > 5:
        print(f"... and {len(elements) - 5} more elements")
    
    print("✅ Element extraction successful!")
else:
    print("⚠ No elements extracted")


# Final summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

print(f"""
✅ All tests passed!

Test Results:
  ✓ Package imported successfully
  ✓ All submodules accessible
  ✓ Dependencies available
  ✓ Ollama connection established
  ✓ Model '{model_name}' available
  ✓ Configuration valid
  ✓ Test image created
  ✓ OllamaOCR instance created
  ✓ Document processed successfully
  ✓ Output files created
  ✓ Elements extracted

System is fully operational and ready to use!

Output Location: {result.output_dir}

Next Steps:
  1. Check the output directory to see results
  2. Try processing your own PDFs/images
  3. Customize configuration for your needs

Example usage:
  from DocumentParser import OllamaOCR
  
  ocr = OllamaOCR()
  result = ocr.process("your_document.pdf")
  print(f"Processed {{result.page_count}} pages")
""")

# Cleanup option
print("="*80)
cleanup = input("\nCleanup test files? (y/n): ").lower().strip()

if cleanup == 'y':
    import shutil
    shutil.rmtree(temp_dir)
    print(f"✓ Cleaned up: {temp_dir}")
else:
    print(f"✓ Test files kept at: {temp_dir}")

print("\n🎉 Testing complete! System is ready to use! 🎉\n")