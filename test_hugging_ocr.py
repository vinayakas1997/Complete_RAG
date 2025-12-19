"""
Test HuggingFaceOCR - Fast OCR Processing
Test with your documents using HuggingFace transformers.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import HuggingFaceOCR (add this to your DocumentParser package)
# For now, we'll assume it's been added to main.py
try:
    from DocumentParser import HuggingFaceOCR
except ImportError:
    print("⚠️  HuggingFaceOCR not found in DocumentParser package")
    print("Please add the HuggingFace files to your package first.")
    print("\nSee installation instructions in the script comments.")
    sys.exit(1)

print("="*80)
print("HUGGINGFACE OCR TEST - HIGH PERFORMANCE")
print("="*80)

# ========== CONFIGURE YOUR SETTINGS HERE ==========
YOUR_FILE = r"dont_send\02AC001(1)：下野部工場　機密区域管理要領_single_page_3.pdf"
OUTPUT_DIR = "hugging-face-02AC001-single-page-3-test-single-filesystem-trail3"
DEVICE = "cuda:0"  # or "cuda:1" or "cpu"

# Custom cache directory (set to None for default)
# Example: Store models on D: drive to save C: drive space
CACHE_DIR = "D:/AI_Models/huggingface"  # Change to "D:/AI_Models/huggingface" if desired
# CACHE_DIR = "D:/AI_Models/huggingface"
# ==================================================

print(f"\nSettings:")
print(f"  Device: {DEVICE}")
print(f"  Cache: {CACHE_DIR or 'default (~/.cache/huggingface)'}")
print(f"  Output: {OUTPUT_DIR}")

# Check if file exists
file_path = Path(YOUR_FILE)

if not file_path.exists():
    print(f"\n❌ File not found: {YOUR_FILE}")
    print("\nPlease update YOUR_FILE in the script.")
    sys.exit(1)

print(f"\n✓ Test file: {file_path.name}")
print(f"  Size: {file_path.stat().st_size:,} bytes")
print(f"  Type: {file_path.suffix}")

# Create HuggingFaceOCR instance
print("\n" + "="*80)
print("INITIALIZING HUGGINGFACE OCR")
print("="*80)

try:
    start_init = datetime.now()
    
    ocr = HuggingFaceOCR(
        device=DEVICE,
        output_dir=OUTPUT_DIR,
        save_annotations=True,
        cache_dir=CACHE_DIR,
        image_size=1024
    )
    
    init_time = (datetime.now() - start_init).total_seconds()
    
    print(f"\n✓ Initialization complete in {init_time:.2f}s")
    
    # Show info
    info = ocr.get_info()
    print("\nOCR Configuration:")
    print(f"  Type: {info['ocr_type']}")
    print(f"  Model: {info['model']}")
    print(f"  Device: {info['device']}")
    print(f"  Image size: {info['image_size']}")
    print(f"  Cache: {info['cache_dir'] or 'default'}")
    print(f"  Output: {info['output_dir']}")

except Exception as e:
    print(f"\n❌ Failed to initialize: {e}")
    print("\nCommon issues:")
    print("  1. CUDA not available → Use device='cpu'")
    print("  2. Out of memory → Close other GPU applications")
    print("  3. Model not cached → First run will download (~3GB)")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Process document
print("\n" + "="*80)
print("PROCESSING DOCUMENT")
print("="*80)

try:
    process_start = datetime.now()
    
    result = ocr.process(
        file_path=str(file_path),
        verbose=True
    )
    
    process_time = (datetime.now() - process_start).total_seconds()
    
    if result.success:
        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print("="*80)
        print(f"Pages processed: {result.page_count}")
        print(f"Total elements: {result.get_total_elements()}")
        print(f"Processing time: {process_time:.2f}s")
        print(f"Output directory: {result.output_dir}")
        
        # Speed comparison
        print("\n" + "-"*80)
        print("Performance Metrics:")
        print("-"*80)
        print(f"  Average per page: {process_time / result.page_count:.2f}s")
        
        # Expected Ollama time for comparison
        expected_ollama_time = result.page_count * 66  # 66s per page (your baseline)
        speedup = expected_ollama_time / process_time
        
        print(f"\n  Estimated Ollama time: {expected_ollama_time:.0f}s")
        print(f"  HuggingFace time: {process_time:.0f}s")
        print(f"  ⚡ Speed improvement: {speedup:.1f}x faster!")
        
        # Show element breakdown
        print("\n" + "-"*80)
        print("Element Breakdown:")
        print("-"*80)
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
        
        # Verify output files
        print("\n" + "="*80)
        print("Verifying Output Files (Page 1):")
        print("="*80)
        
        output_dir = Path(result.output_dir)
        page_001_dir = output_dir / "pages" / "page_001"
        
        if page_001_dir.exists():
            from PIL import Image
            
            expected_files = {
                'raw_output.txt': page_001_dir / 'raw_output.txt',
                'grounding.json': page_001_dir / 'grounding.json',
                'page_001.md': page_001_dir / 'page_001.md',
                'page_001_original.png': page_001_dir / 'page_001_original.png',
                'page_001_annotated.png': page_001_dir / 'page_001_annotated.png',
                'page_001_comparison.png': page_001_dir / 'page_001_comparison.png',
            }
            
            for name, file_path_check in expected_files.items():
                if file_path_check.exists():
                    size = file_path_check.stat().st_size
                    print(f"  ✓ {name:25s} - {size:>10,} bytes")
                else:
                    print(f"  ✗ {name:25s} - NOT FOUND")
            
            # Check image dimensions
            print("\n  📐 Image dimensions:")
            img_files = {
                'original': page_001_dir / 'page_001_original.png',
                'annotated': page_001_dir / 'page_001_annotated.png',
                'comparison': page_001_dir / 'page_001_comparison.png',
            }
            
            for name, img_path in img_files.items():
                if img_path.exists():
                    img = Image.open(img_path)
                    print(f"    {name:12s}: {img.width:4d} x {img.height:4d} pixels")
        
        else:
            print(f"  ⚠ Page directory not found: {page_001_dir}")
        
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

print("\n" + "="*80)
print("🎉 HUGGINGFACE OCR TEST COMPLETE!")
print("="*80)
print(f"\nTotal time: {process_time:.2f}s")
print(f"Average per page: {process_time / result.page_count:.2f}s")
print(f"Output: {Path(result.output_dir).absolute()}")

print("\n" + "-"*80)
print("Next Steps:")
print("-"*80)
print("1. Check comparison images to verify bounding boxes")
print("2. Compare speed with Ollama version")
print("3. Use HuggingFaceOCR for production processing")
print("4. Enjoy 5-10x faster processing! ⚡")
print()

# ========== INSTALLATION INSTRUCTIONS ==========
"""
INSTALLATION GUIDE FOR HUGGINGFACE OCR
======================================

Step 1: Install Dependencies
-----------------------------
pip install transformers torch
pip install flash-attn  # Optional, for extra speed

Step 2: Add Files to DocumentParser Package
-------------------------------------------
1. Copy huggingface_extractor.py to:
   DocumentParser/extractors/huggingface_extractor.py

2. Add to DocumentParser/extractors/__init__.py:
   
   try:
       from .huggingface_extractor import HuggingFaceExtractor
       HUGGINGFACE_AVAILABLE = True
   except ImportError:
       HUGGINGFACE_AVAILABLE = False
   
   # Add to __all__
   if HUGGINGFACE_AVAILABLE:
       __all__.append('HuggingFaceExtractor')

3. Add HuggingFaceOCR class to DocumentParser/main.py:
   (Copy the class from huggingface_ocr_main.py)

4. Add to DocumentParser/__init__.py:
   
   try:
       from .main import HuggingFaceOCR
       __all__.append('HuggingFaceOCR')
   except ImportError:
       pass

Step 3: Custom Cache Directory on D: Drive (Optional)
-----------------------------------------------------
To save C: drive space, store models on D: drive:

# Option 1: In code
ocr = HuggingFaceOCR(cache_dir="D:/AI_Models/huggingface")

# Option 2: Environment variable (permanent)
# Add to Windows environment variables:
TRANSFORMERS_CACHE=D:\\AI_Models\\huggingface
HF_HOME=D:\\AI_Models\\huggingface

Step 4: First Run
-----------------
First run will download model weights (~3GB)
This happens automatically and only once.

Step 5: Usage
-------------
from DocumentParser import HuggingFaceOCR

# Basic usage
ocr = HuggingFaceOCR()
result = ocr.process("document.pdf")

# With custom cache
ocr = HuggingFaceOCR(cache_dir="D:/AI_Models")
result = ocr.process("document.pdf")

# Specific GPU
ocr = HuggingFaceOCR(device="cuda:1")
result = ocr.process("document.pdf")

DONE! You're ready to use HuggingFaceOCR! 🚀
"""