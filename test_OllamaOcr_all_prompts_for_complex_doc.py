"""
Prompt Optimization Test Script
Test different prompts and compare results with full visualization.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from DocumentParser import OllamaOCR
from DocumentParser.config import get_full_output_config, OCRConfig
from PIL import Image

print("="*80)
print("PROMPT OPTIMIZATION TEST")
print("="*80)

# ========== CONFIGURE YOUR TEST FILE HERE ==========
TEST_FILE = r"dont_send\M1-AM-STB3-25001 (1)_single_page_1st.pdf"
BASE_OUTPUT_DIR = "prompt_test_results"
# ====================================================

# Check if file exists
file_path = Path(TEST_FILE)

if not file_path.exists():
    print(f"\n❌ File not found: {TEST_FILE}")
    print("\nPlease update TEST_FILE in the script.")
    sys.exit(1)

print(f"\n✓ Test file: {file_path.name}")
print(f"  Size: {file_path.stat().st_size:,} bytes")

# Define prompts to test
PROMPTS = {
    "cycle1_original": {
        "description": "Original default prompt - converts to markdown",
        "prompt": "<image>\n<|grounding|>Convert the document to markdown."
    },
    
    "cycle2_table_focused": {
        "description": "Table-focused - extracts complete tables with rows",
        "prompt": """<image>
<|grounding|>Extract the document structure focusing on:
1. Complete tables with all rows and columns
2. Table headers and section titles
3. Form fields and their values
4. Group related content together
Preserve table relationships and structure."""
    },
    
    "cycle3_hierarchical": {
        "description": "Hierarchical structure - organized by document hierarchy",
        "prompt": """<image>
<|grounding|>Extract document with hierarchical structure:
- Main titles and section headers
- Complete tables (not individual cells)
- Form sections and fields
- Maintain logical reading order
Output structured content with clear relationships."""
    },
    
    "cycle4_grouped": {
        "description": "Grouped elements - reduces fragmentation",
        "prompt": """<image>
<|grounding|>Extract document with grouped elements:
- Combine related text into paragraphs
- Extract complete tables (not individual cells)
- Group form sections together
- Merge adjacent text boxes
Maintain document structure while reducing element count."""
    },
    
    "cycle5_japanese": {
        "description": "Japanese-optimized - uses Japanese instructions",
        "prompt": """<image>
<|grounding|>文書構造を抽出してください：
1. 表のヘッダーとセクション
2. 完全な表の行（全ての列を含む）
3. フォームフィールドと値
4. 関連するコンテンツをグループ化
テーブル構造を保持し、マークダウン形式で出力。"""
    },
    
    "cycle6_simplified": {
        "description": "Simplified - focuses on main structure only",
        "prompt": """<image>
<|grounding|>Extract main document structure:
- Document title
- Section headers
- Tables (as complete units)
- Key form fields
Ignore minor text fragments. Focus on major structural elements."""
    }
}

print(f"\n📋 Will test {len(PROMPTS)} different prompts")
print("-"*80)

# Store results for comparison
all_results = {}
test_start_time = datetime.now()

# Test each prompt
for cycle_name, prompt_info in PROMPTS.items():
    print("\n" + "="*80)
    print(f"🔬 TESTING: {cycle_name}")
    print("="*80)
    print(f"Description: {prompt_info['description']}")
    print(f"Prompt: {prompt_info['prompt'][:100]}...")
    print("-"*80)
    
    # Create output directory for this cycle
    cycle_output_dir = f"{BASE_OUTPUT_DIR}/{cycle_name}"
    
    try:
        # Create OCR instance with FULL output config
        output_config = get_full_output_config()
        
        ocr_config = OCRConfig(
            model_name="deepseek-ocr:3b",
            output_config=output_config,
            output_dir=cycle_output_dir
        )
        
        ocr = OllamaOCR(config=ocr_config)
        
        print(f"✓ OCR instance created for {cycle_name}")
        print(f"  Output directory: {cycle_output_dir}")
        
        # Process document with custom prompt
        result = ocr.process(
            file_path=str(file_path),
            custom_prompt=prompt_info['prompt'],
            verbose=True
        )
        
        # Store results
        all_results[cycle_name] = {
            'result': result,
            'description': prompt_info['description'],
            'prompt': prompt_info['prompt']
        }
        
        if result.success:
            print(f"\n✓ SUCCESS: {cycle_name}")
            print(f"  Pages: {result.page_count}")
            print(f"  Total elements: {result.get_total_elements()}")
            print(f"  Processing time: {result.total_processing_time:.2f}s")
            
            # Show element breakdown
            element_types = {}
            for page_result in result.page_results:
                for element in page_result.extraction_result.get_elements():
                    elem_type = element.element_type
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            print("\n  Element breakdown:")
            for elem_type, count in sorted(element_types.items()):
                print(f"    {elem_type:15s}: {count:3d}")
            
            # Verify output files for page 1
            output_dir = Path(result.output_dir)
            page_001_dir = output_dir / "pages" / "page_001"
            
            if page_001_dir.exists():
                print("\n  ✓ Output files generated:")
                
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
                        print(f"    ✓ {name:25s} - {size:>10,} bytes")
                    else:
                        print(f"    ✗ {name:25s} - NOT FOUND")
                
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
            print(f"\n✗ FAILED: {cycle_name}")
            print(f"  Error: {result.error_message}")
    
    except Exception as e:
        print(f"\n✗ EXCEPTION in {cycle_name}")
        print(f"  Error: {str(e)}")
        import traceback
        traceback.print_exc()

test_end_time = datetime.now()
total_test_time = (test_end_time - test_start_time).total_seconds()

# Generate comparison report
print("\n" + "="*80)
print("📊 COMPARISON REPORT")
print("="*80)

if all_results:
    print(f"\nTotal test time: {total_test_time:.2f}s")
    print(f"Cycles tested: {len(all_results)}")
    
    print("\n" + "-"*80)
    print("Summary by Cycle:")
    print("-"*80)
    print(f"{'Cycle':20s} | {'Status':8s} | {'Pages':5s} | {'Elements':8s} | {'Time':8s}")
    print("-"*80)
    
    for cycle_name, data in all_results.items():
        result = data['result']
        if result.success:
            status = "✓ OK"
            pages = str(result.page_count)
            elements = str(result.get_total_elements())
            time_str = f"{result.total_processing_time:.2f}s"
        else:
            status = "✗ FAIL"
            pages = "-"
            elements = "-"
            time_str = "-"
        
        print(f"{cycle_name:20s} | {status:8s} | {pages:5s} | {elements:8s} | {time_str:8s}")
    
    # Find best result (least elements = less fragmentation)
    successful_results = {k: v for k, v in all_results.items() if v['result'].success}
    
    if successful_results:
        print("\n" + "-"*80)
        print("Element Count Comparison (Lower = Less Fragmentation):")
        print("-"*80)
        
        sorted_by_elements = sorted(
            successful_results.items(),
            key=lambda x: x[1]['result'].get_total_elements()
        )
        
        for rank, (cycle_name, data) in enumerate(sorted_by_elements, 1):
            result = data['result']
            elements = result.get_total_elements()
            
            if rank == 1:
                badge = "🏆 BEST"
            elif rank == 2:
                badge = "🥈 2nd"
            elif rank == 3:
                badge = "🥉 3rd"
            else:
                badge = f"   {rank}th"
            
            print(f"{badge} {cycle_name:20s}: {elements:3d} elements")
        
        # Detailed comparison
        print("\n" + "-"*80)
        print("Detailed Element Type Comparison:")
        print("-"*80)
        
        # Collect all element types
        all_types = set()
        cycle_type_counts = {}
        
        for cycle_name, data in successful_results.items():
            result = data['result']
            element_types = {}
            
            for page_result in result.page_results:
                for element in page_result.extraction_result.get_elements():
                    elem_type = element.element_type
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
                    all_types.add(elem_type)
            
            cycle_type_counts[cycle_name] = element_types
        
        # Print table header
        header = f"{'Element Type':15s} | "
        for cycle_name in successful_results.keys():
            header += f"{cycle_name[:15]:15s} | "
        print(header)
        print("-" * len(header))
        
        # Print each element type
        for elem_type in sorted(all_types):
            row = f"{elem_type:15s} | "
            for cycle_name in successful_results.keys():
                count = cycle_type_counts[cycle_name].get(elem_type, 0)
                row += f"{count:15d} | "
            print(row)

# Generate recommendation
print("\n" + "="*80)
print("💡 RECOMMENDATIONS")
print("="*80)

if successful_results:
    best_cycle = sorted_by_elements[0][0]
    best_result = sorted_by_elements[0][1]['result']
    best_desc = sorted_by_elements[0][1]['description']
    
    print(f"\n🏆 Best prompt: {best_cycle}")
    print(f"   Description: {best_desc}")
    print(f"   Elements: {best_result.get_total_elements()}")
    print(f"   Processing time: {best_result.total_processing_time:.2f}s")
    
    print("\n📁 Check visual results:")
    for cycle_name in successful_results.keys():
        result = successful_results[cycle_name]['result']
        output_dir = Path(result.output_dir) / "pages" / "page_001"
        comparison_path = output_dir / "page_001_comparison.png"
        
        if comparison_path.exists():
            print(f"\n  {cycle_name}:")
            print(f"    {comparison_path.absolute()}")
    
    print("\n" + "-"*80)
    print("Next Steps:")
    print("-"*80)
    print("1. Open comparison images above to visually inspect bounding boxes")
    print("2. Compare element counts - lower is usually better")
    print("3. Check if important elements are captured")
    print("4. Choose best prompt for your use case")
    print(f"5. Update your production code to use the best prompt")
    
    print("\n" + "-"*80)
    print("How to use best prompt in production:")
    print("-"*80)
    print(f"""
# In your production code:
ocr = OllamaOCR()

custom_prompt = '''{all_results[best_cycle]['prompt']}'''

result = ocr.process(
    "your_document.pdf",
    custom_prompt=custom_prompt
)
""")

else:
    print("\n⚠ No successful results to compare.")
    print("Please check errors above and ensure:")
    print("  1. Ollama is running")
    print("  2. Model is available (deepseek-ocr:3b)")
    print("  3. Test file exists and is readable")

# Final output structure
print("\n" + "="*80)
print("📂 OUTPUT STRUCTURE")
print("="*80)
print(f"""
{BASE_OUTPUT_DIR}/
├── cycle1_original/
│   └── {file_path.stem}/
│       ├── pages/
│       │   └── page_001/
│       │       ├── raw_output.txt
│       │       ├── grounding.json
│       │       ├── page_001.md
│       │       ├── page_001_original.png
│       │       ├── page_001_annotated.png      ← Check boxes here!
│       │       └── page_001_comparison.png     ← Side-by-side view!
│       ├── combined/
│       └── metadata.json
├── cycle2_table_focused/
│   └── ... (same structure)
├── cycle3_hierarchical/
├── cycle4_grouped/
├── cycle5_japanese/
└── cycle6_simplified/

All outputs saved to: {Path(BASE_OUTPUT_DIR).absolute()}
""")

print("="*80)
print("🎉 TEST COMPLETE!")
print("="*80)
print(f"\nTotal execution time: {total_test_time:.2f}s")
print(f"Results saved to: {Path(BASE_OUTPUT_DIR).absolute()}")
print("\nNext: Open comparison images to visually compare bounding boxes!\n")