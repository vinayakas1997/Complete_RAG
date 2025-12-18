"""
Test OCR System with Your Own File
Simple script to test with real documents.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from DocumentParser import OllamaOCR
from DocumentParser.config import get_full_output_config, OCRConfig

print("="*80)
print("TESTING WITH YOUR FILE")
print("="*80)

# ========== CONFIGURE YOUR FILE HERE ==========
YOUR_FILE = r"test_files\02AC001：下野部工場　機密区域管理要領\02AC001(1)：下野部工場　機密区域管理要領.pdf"
OUTPUT_DIR = "shimonobe1-trail2"
# YOUR_FILE = "test.pdf"
# OUTPUT_DIR = "new-output-trail-4"
# ==============================================

# Check if file exists
file_path = Path(YOUR_FILE)

if not file_path.exists():
    print(f"\n❌ File not found: {YOUR_FILE}")
    print("\nPlease update YOUR_FILE in the script to point to your document.")
    print(f"Current directory: {Path.cwd()}")
    sys.exit(1)

print(f"\n✓ File found: {file_path.name}")
print(f"  Size: {file_path.stat().st_size:,} bytes")
print(f"  Type: {file_path.suffix}")

# Create OCR instance
print("\n" + "-"*80)
print("Creating OllamaOCR instance...")
print("-"*80)

try:
    # ========== USE FULL OUTPUT CONFIG ==========
    output_config = get_full_output_config()
    # output_config.output_base_dir = OUTPUT_DIR  # Set custom output dir
    
    # Create OCR config
    ocr_config = OCRConfig(
        model_name="deepseek-ocr:3b",
        output_config=output_config,
        output_dir=OUTPUT_DIR
    )
    
    # Create OCR instance with full config
    ocr = OllamaOCR(config=ocr_config)
    # ===========================================
    
    # Show configuration
    print("✓ OCR instance created")
    print(f"  Model: {ocr.config.model_name}")
    print(f"  Output: {ocr.config.output_config.output_base_dir}")
    print(f"  Grounding: {ocr.config.use_grounding}")
    print(f"  Save annotations: {ocr.config.output_config.save_per_page['annotated_image']}")
    print(f"  Create comparison: {ocr.config.output_config.create_comparison}")

except Exception as e:
    print(f"❌ Failed to create OCR instance: {e}")
    print("\nMake sure:")
    print("  1. Ollama is running: ollama serve")
    print("  2. Model is available: ollama list")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Process the document
print("\n" + "="*80)
print("PROCESSING DOCUMENT")
print("="*80)

try:
    result = ocr.process(
        file_path=str(file_path),
        verbose=True  # Shows progress
    )
    
    if result.success:
        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print("="*80)
        print(f"Pages processed: {result.page_count}")
        print(f"Total elements: {result.get_total_elements()}")
        print(f"Processing time: {result.total_processing_time:.2f}s")
        print(f"Output directory: {result.output_dir}")
        
        # Show element breakdown by type
        print("\nElement Breakdown:")
        element_types = {}
        for page_result in result.page_results:
            for element in page_result.extraction_result.get_elements():
                elem_type = element.element_type
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        for elem_type, count in sorted(element_types.items()):
            print(f"  {elem_type:15s}: {count:3d}")
        
        # Show failed pages if any
        failed_pages = result.get_failed_pages()
        if failed_pages:
            print(f"\n⚠ Failed pages: {failed_pages}")
        
        # ========== VERIFY OUTPUT FILES ==========
        print("\n" + "="*80)
        print("Verifying Output Files (Page 1):")
        print("="*80)
        
        output_dir = Path(result.output_dir)
        page_001_dir = output_dir / "pages" / "page_001"
        
        if page_001_dir.exists():
            expected_files = {
                'raw_output.txt': page_001_dir / 'raw_output.txt',
                'grounding.json': page_001_dir / 'grounding.json',
                'page_001.md': page_001_dir / 'page_001.md',
                'page_001_annotated.png': page_001_dir / 'page_001_annotated.png',
                'page_001_comparison.png': page_001_dir / 'page_001_comparison.png',
                'page_001_original.png': page_001_dir / 'page_001_original.png',
            }
            
            for name, file_path in expected_files.items():
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"  ✓ {name:25s} - {size:>10,} bytes")
                else:
                    print(f"  ✗ {name:25s} - NOT FOUND")
        else:
            print(f"  ⚠ Page directory not found: {page_001_dir}")
        # =========================================
        
        print("\n" + "="*80)
        print("Check output directory for results:")
        print(f"  {output_dir.absolute()}")
        print("="*80)
    
    else:
        print(f"\n❌ Processing failed: {result.error_message}")
        sys.exit(1)

except Exception as e:
    print(f"\n❌ Error during processing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Done! Check the output directory for your results.\n")

# After processing, check image dimensions
from PIL import Image

output_dir = Path(result.output_dir)
page_dir = output_dir / "pages" / "page_001"

# Check all image files
image_files = {
    'original': page_dir / 'page_001_original.png',
    'annotated': page_dir / 'page_001_annotated.png',
    'comparison': page_dir / 'page_001_comparison.png',
}

print("\n" + "="*80)
print("Image Dimensions:")
print("="*80)

for name, img_path in image_files.items():
    if img_path.exists():
        img = Image.open(img_path)
        print(f"  {name:15s}: {img.width} x {img.height} pixels")
    else:
        print(f"  {name:15s}: NOT FOUND")

# Also check the temp page image
temp_pages = output_dir / "temp_pages"
if temp_pages.exists():
    temp_img = list(temp_pages.glob("page_001.png"))
    if temp_img:
        img = Image.open(temp_img[0])
        print(f"  {'temp_page':15s}: {img.width} x {img.height} pixels")