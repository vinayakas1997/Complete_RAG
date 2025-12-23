"""
Comparison Image to PDF Converter
Collects all page_XXX_comparison.png files and creates a single PDF report.

Usage:
    python create_comparison_pdf.py "output_folder_path"
    
Example:
    python create_comparison_pdf.py "prompt_analysis/default_20251223_171329"
    
Output:
    Creates: default_20251223_171329.pdf in same directory
"""

import sys
from pathlib import Path
from PIL import Image
import argparse

def collect_comparison_images(base_folder):
    """
    Collect all comparison images from folder structure.
    
    Structure expected:
        base_folder/
        └── document_name/
            └── pages/
                ├── page_001/
                │   └── page_001_comparison.png
                ├── page_002/
                │   └── page_002_comparison.png
                └── ...
    
    Returns:
        List of (page_number, image_path) tuples, sorted by page number
    """
    base_path = Path(base_folder)
    
    if not base_path.exists():
        print(f"❌ Folder not found: {base_folder}")
        return []
    
    print(f"📁 Scanning: {base_folder}")
    
    # Find all comparison images
    comparison_images = []
    
    # Look in pages folders
    pages_folders = list(base_path.glob("**/pages"))
    
    if not pages_folders:
        print("⚠️  No 'pages' folder found")
        return []
    
    for pages_folder in pages_folders:
        print(f"  Checking: {pages_folder}")
        
        # Find all page_XXX folders
        page_folders = sorted(pages_folder.glob("page_*"))
        
        for page_folder in page_folders:
            # Extract page number
            page_name = page_folder.name  # e.g., "page_001"
            page_num = int(page_name.split('_')[1])  # Extract 001 -> 1
            
            # Look for comparison image
            comparison_file = page_folder / f"{page_name}_comparison.png"
            
            if comparison_file.exists():
                comparison_images.append((page_num, comparison_file))
                print(f"    ✓ Found: {comparison_file.name}")
            else:
                print(f"    ✗ Missing: {comparison_file.name}")
    
    # Sort by page number
    comparison_images.sort(key=lambda x: x[0])
    
    return comparison_images


def create_pdf_from_images(images, output_pdf):
    """
    Create PDF from list of images.
    
    Args:
        images: List of (page_number, image_path) tuples
        output_pdf: Output PDF file path
    """
    if not images:
        print("❌ No images to process")
        return False
    
    print(f"\n📄 Creating PDF with {len(images)} pages...")
    
    try:
        # Open all images
        pil_images = []
        
        for page_num, img_path in images:
            print(f"  Processing page {page_num}...")
            img = Image.open(img_path)
            
            # Convert to RGB if necessary (PDF requires RGB)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            pil_images.append(img)
        
        # Save as PDF
        if len(pil_images) == 1:
            pil_images[0].save(output_pdf)
        else:
            pil_images[0].save(
                output_pdf,
                save_all=True,
                append_images=pil_images[1:],
                resolution=100.0,
                quality=95
            )
        
        print(f"\n✅ PDF created: {output_pdf}")
        print(f"   Pages: {len(images)}")
        print(f"   Size: {Path(output_pdf).stat().st_size:,} bytes")
        
        return True
    
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(
        description="Create PDF from comparison images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_comparison_pdf.py "output/my_document"
  python create_comparison_pdf.py "prompt_analysis/default_20251223_171329"
  
Output:
  Creates PDF with name from parent folder:
    "output/my_document" → "my_document.pdf"
    "prompt_analysis/default_20251223_171329" → "default_20251223_171329.pdf"
        """
    )
    
    parser.add_argument(
        'folder',
        help='Path to folder containing comparison images'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output PDF filename (optional, auto-generated if not provided)'
    )
    
    args = parser.parse_args()
    
    folder_path = Path(args.folder)
    
    print("="*80)
    print("COMPARISON IMAGES TO PDF CONVERTER")
    print("="*80)
    
    # Collect images
    images = collect_comparison_images(folder_path)
    
    if not images:
        print("\n❌ No comparison images found!")
        print("\nExpected structure:")
        print("  folder/")
        print("  └── document_name/")
        print("      └── pages/")
        print("          ├── page_001/")
        print("          │   └── page_001_comparison.png")
        print("          └── page_002/")
        print("              └── page_002_comparison.png")
        sys.exit(1)
    
    # Generate output filename
    if args.output:
        output_pdf = Path(args.output)
    else:
        # Use parent folder name
        folder_name = folder_path.name
        output_pdf = folder_path.parent / f"{folder_name}.pdf"
    
    print(f"\n📝 Output PDF: {output_pdf}")
    
    # Create PDF
    success = create_pdf_from_images(images, output_pdf)
    
    if success:
        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print("="*80)
        print(f"PDF created: {output_pdf.absolute()}")
        print(f"\nOpen with: start {output_pdf}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    # If no arguments, show usage
    if len(sys.argv) == 1:
        print("="*80)
        print("COMPARISON IMAGES TO PDF CONVERTER")
        print("="*80)
        print("\nUsage:")
        print("  python create_comparison_pdf.py <folder_path>")
        print("\nExample:")
        print("  python create_comparison_pdf.py \"output/my_document\"")
        print("  python create_comparison_pdf.py \"prompt_analysis/default_20251223_171329\"")
        print("\nWhat it does:")
        print("  1. Scans folder for all page_XXX_comparison.png files")
        print("  2. Collects them in order")
        print("  3. Creates a single PDF")
        print("  4. Names PDF after the parent folder")
        print("\nOutput example:")
        print("  Input:  prompt_analysis/default_20251223_171329/")
        print("  Output: prompt_analysis/default_20251223_171329.pdf")
        print("\n" + "="*80)
        sys.exit(0)
    
    main()