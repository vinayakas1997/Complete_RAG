"""
Prompt Testing & Analysis Script
Test multiple prompts and compare results automatically.
"""

import sys
from pathlib import Path
from datetime import datetime
import json
from PIL import Image

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from DocumentParser import OllamaOCR
from DocumentParser.config import get_full_output_config, OCRConfig

print("="*80)
print("PROMPT TESTING & ANALYSIS")
print("="*80)

# ========== CONFIGURE YOUR FILE HERE ==========
# YOUR_FILE = r"dont_send\02AC001(1)：下野部工場　機密区域管理要領.pdf"
# YOUR_FILE = r"dont_send/02AC001(1)：下野部工場　機密区域管理要領_single_3.pdf"
# YOUR_FILE = r"dont_send\M1-AM-STB3-25001-single-page(1).pdf"
# BASE_OUTPUT_DIR = "prompt_analysis5_complete_file_shimo1_baseline_4_prompts"  # Dynamic folders will be created
YOUR_FILE = r"dont_send\test_files\21AC001：電気事業法　下野部工場保安規程\21AC001(2)：電気事業法　下野部工場保安規程.pdf"
BASE_OUTPUT_DIR = "prompt_analysis8_shimonobe_file2"
# ==============================================

# ========== PROMPTS TO TEST ==========
TEST_PROMPTS = {
    # "default": {
    #     "prompt": "<image>\n<|grounding|>Convert the document to markdown.",
    #     "description": "Default DeepSeek prompt",
    #     "difficulty": "Simple",
    #     "expected_speed": "Fast (30-45s)",
    #     "best_for": "General documents"
    # },
    
    "table_focused": {
        "prompt": "<image>\n<|grounding|>Extract all text and tables from this document in markdown format. Include complete table structures with all headers and data rows.",
        "description": "Table-focused extraction",
        "difficulty": "Medium",
        "expected_speed": "Medium (40-60s)",
        "best_for": "Documents with tables"
    },
    
    "comprehensive": {
        "prompt": "<image>\n<|grounding|>Extract all text and tables from this document in markdown format. Include complete table structures with all headers and data rows. Preserve document layout and hierarchy.",
        "description": "Comprehensive extraction",
        "difficulty": "Medium-High",
        "expected_speed": "Medium-Slow (45-70s)",
        "best_for": "Complex documents"
    },
    
    # "detailed": {
    #     "prompt": "<image>\n<|grounding|>Extract complete document content: 1) All tables with full structure 2) All text sections 3) Headers and titles 4) Lists and captions. Maintain document organization.",
    #     "description": "Detailed extraction with structure",
    #     "difficulty": "High",
    #     "expected_speed": "Slow (50-80s)",
    #     "best_for": "Complex layouts with multiple element types"
    # },
    
    # "manufacturing": {
    #     "prompt": "<image>\n<|grounding|>Extract all text and tables from this manufacturing document. Capture complete table structures with headers, data rows, and captions. Preserve document hierarchy and layout.",
    #     "description": "Manufacturing-specific extraction",
    #     "difficulty": "Medium-High",
    #     "expected_speed": "Medium-Slow (45-70s)",
    #     "best_for": "Manufacturing documents with tables and technical content"
    # },
    
    # "japanese_focused": {
    #     "prompt": "<image>\n<|grounding|>この文書から全てのテキストと表を抽出してください。完全な表構造を含めてください。",
    #     "description": "Japanese-optimized prompt",
    #     "difficulty": "Medium",
    #     "expected_speed": "Medium (40-60s)",
    #     "best_for": "Japanese documents"
    # }
}
# ======================================

# Check if file exists
file_path = Path(YOUR_FILE)

if not file_path.exists():
    print(f"\n❌ File not found: {YOUR_FILE}")
    print("\nPlease update YOUR_FILE in the script.")
    sys.exit(1)

print(f"\n✓ Test file: {file_path.name}")
print(f"  Size: {file_path.stat().st_size:,} bytes")
print(f"  Type: {file_path.suffix}")
print(f"\n📋 Testing {len(TEST_PROMPTS)} different prompts...")

# Store results
all_results = {}
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Process each prompt
for prompt_name, prompt_info in TEST_PROMPTS.items():
    print("\n" + "="*80)
    print(f"🔬 TESTING: {prompt_name}")
    print("="*80)
    print(f"Description: {prompt_info['description']}")
    print(f"Difficulty: {prompt_info['difficulty']}")
    print(f"Expected: {prompt_info['expected_speed']}")
    print(f"Best for: {prompt_info['best_for']}")
    print("-"*80)
    
    # Create dynamic output directory
    output_dir = f"{BASE_OUTPUT_DIR}/{prompt_name}_{timestamp}"
    
    try:
        # Create OCR instance
        output_config = get_full_output_config()
        
        ocr_config = OCRConfig(
            model_name="deepseek-ocr:3b",
            output_config=output_config,
            output_dir=output_dir
        )
        
        ocr = OllamaOCR(config=ocr_config)
        
        print(f"✓ OCR instance created")
        print(f"  Output: {output_dir}")
        
        # Process document
        start_time = datetime.now()
        
        result = ocr.process(
            file_path=str(file_path),
            custom_prompt=prompt_info['prompt'],
            verbose=False  # Reduce clutter
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        if result.success:
            # Analyze results
            element_types = {}
            for page_result in result.page_results:
                for element in page_result.extraction_result.get_elements():
                    elem_type = element.element_type
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            # Count specific elements
            table_count = element_types.get('table', 0)
            text_count = element_types.get('text', 0)
            title_count = element_types.get('title', 0) + element_types.get('sub_title', 0)
            image_count = element_types.get('image', 0)
            
            # Store results
            all_results[prompt_name] = {
                'success': True,
                'processing_time': processing_time,
                'total_elements': result.get_total_elements(),
                'element_breakdown': element_types,
                'table_count': table_count,
                'text_count': text_count,
                'title_count': title_count,
                'image_count': image_count,
                'output_dir': output_dir,
                'prompt_info': prompt_info
            }
            
            # Print results
            print(f"\n✅ SUCCESS")
            print(f"  ⏱️  Processing time: {processing_time:.2f}s")
            print(f"  📊 Total elements: {result.get_total_elements()}")
            print(f"\n  Element breakdown:")
            for elem_type, count in sorted(element_types.items()):
                print(f"    {elem_type:15s}: {count:3d}")
            
            print(f"\n  📁 Output: {output_dir}")
        
        else:
            all_results[prompt_name] = {
                'success': False,
                'error': result.error_message,
                'processing_time': processing_time,
                'prompt_info': prompt_info
            }
            
            print(f"\n❌ FAILED")
            print(f"  Error: {result.error_message}")
    
    except Exception as e:
        all_results[prompt_name] = {
            'success': False,
            'error': str(e),
            'processing_time': 0,
            'prompt_info': prompt_info
        }
        
        print(f"\n❌ EXCEPTION")
        print(f"  Error: {str(e)}")

# Generate comparison report
print("\n" + "="*80)
print("📊 COMPARISON REPORT")
print("="*80)

# Sort by processing time
successful_results = {k: v for k, v in all_results.items() if v['success']}

if successful_results:
    sorted_by_time = sorted(successful_results.items(), key=lambda x: x[1]['processing_time'])
    
    print("\n⏱️  Speed Ranking (Fastest to Slowest):")
    print("-"*80)
    print(f"{'Rank':5s} {'Prompt':20s} {'Time':10s} {'Elements':10s} {'Tables':8s}")
    print("-"*80)
    
    for rank, (name, data) in enumerate(sorted_by_time, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"  {rank}"
        print(f"{medal:5s} {name:20s} {data['processing_time']:8.2f}s {data['total_elements']:8d}   {data['table_count']:6d}")
    
    # Element detection ranking
    print("\n📊 Element Detection Ranking (Most to Least):")
    print("-"*80)
    print(f"{'Rank':5s} {'Prompt':20s} {'Elements':10s} {'Tables':8s} {'Text':8s} {'Titles':8s}")
    print("-"*80)
    
    sorted_by_elements = sorted(successful_results.items(), key=lambda x: x[1]['total_elements'], reverse=True)
    
    for rank, (name, data) in enumerate(sorted_by_elements, 1):
        medal = "🏆" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"  {rank}"
        print(f"{medal:5s} {name:20s} {data['total_elements']:8d}   {data['table_count']:6d}  {data['text_count']:6d}  {data['title_count']:6d}")
    
    # Table detection ranking
    print("\n📋 Table Detection Ranking:")
    print("-"*80)
    sorted_by_tables = sorted(successful_results.items(), key=lambda x: x[1]['table_count'], reverse=True)
    
    for rank, (name, data) in enumerate(sorted_by_tables, 1):
        print(f"  {rank}. {name:20s}: {data['table_count']} tables")
    
    # Accuracy vs Speed Analysis
    print("\n⚖️  Accuracy vs Speed Analysis:")
    print("-"*80)
    
    # Calculate score: (elements / time) - higher is better
    for name, data in successful_results.items():
        efficiency = data['total_elements'] / data['processing_time']
        data['efficiency_score'] = efficiency
    
    sorted_by_efficiency = sorted(successful_results.items(), key=lambda x: x[1]['efficiency_score'], reverse=True)
    
    print(f"{'Rank':5s} {'Prompt':20s} {'Efficiency':12s} {'Time':10s} {'Elements':10s}")
    print("-"*80)
    
    for rank, (name, data) in enumerate(sorted_by_efficiency, 1):
        score = data['efficiency_score']
        print(f"  {rank}. {name:20s} {score:10.2f}   {data['processing_time']:8.2f}s {data['total_elements']:8d}")
    
    # Best prompt recommendation
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    fastest = sorted_by_time[0]
    most_accurate = sorted_by_elements[0]
    best_efficiency = sorted_by_efficiency[0]
    
    print(f"\n🏃 Fastest: {fastest[0]}")
    print(f"   Time: {fastest[1]['processing_time']:.2f}s")
    print(f"   Use for: Quick processing, simple documents")
    
    print(f"\n🎯 Most Accurate: {most_accurate[0]}")
    print(f"   Elements: {most_accurate[1]['total_elements']}")
    print(f"   Use for: Complex documents, maximum detail")
    
    print(f"\n⚖️  Best Balance: {best_efficiency[0]}")
    print(f"   Efficiency: {best_efficiency[1]['efficiency_score']:.2f}")
    print(f"   Use for: Production workloads")
    
    # Specific recommendations
    print("\n" + "-"*80)
    print("📋 Specific Use Cases:")
    print("-"*80)
    
    # Find best for tables
    best_for_tables = max(successful_results.items(), key=lambda x: x[1]['table_count'])
    print(f"\n  For documents with tables:")
    print(f"    → {best_for_tables[0]}")
    print(f"    Detected {best_for_tables[1]['table_count']} tables in {best_for_tables[1]['processing_time']:.2f}s")
    
    # Find fastest acceptable
    acceptable_threshold = most_accurate[1]['total_elements'] * 0.8  # 80% of max
    fast_and_good = [
        (name, data) for name, data in sorted_by_time 
        if data['total_elements'] >= acceptable_threshold
    ]
    
    if fast_and_good:
        print(f"\n  For production (fast + accurate):")
        print(f"    → {fast_and_good[0][0]}")
        print(f"    {fast_and_good[0][1]['total_elements']} elements in {fast_and_good[0][1]['processing_time']:.2f}s")

# Save detailed report to JSON
report_file = f"{BASE_OUTPUT_DIR}/analysis_report_{timestamp}.json"
Path(BASE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\n📄 Detailed report saved: {report_file}")

# Generate HTML report
html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Prompt Analysis Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #667eea; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .medal {{ font-size: 20px; }}
        .success {{ color: #4caf50; font-weight: bold; }}
        .time {{ color: #2196f3; }}
        .elements {{ color: #ff9800; }}
        .prompt-card {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Prompt Analysis Report</h1>
        <p><strong>Test File:</strong> {file_path.name}</p>
        <p><strong>Timestamp:</strong> {timestamp}</p>
        <p><strong>Prompts Tested:</strong> {len(TEST_PROMPTS)}</p>
        
        <h2>⏱️ Speed Ranking</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Prompt</th>
                <th>Time (s)</th>
                <th>Elements</th>
                <th>Tables</th>
                <th>Efficiency</th>
            </tr>
"""

if successful_results:
    for rank, (name, data) in enumerate(sorted_by_time, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}"
        efficiency = data.get('efficiency_score', 0)
        html_report += f"""
            <tr>
                <td class="medal">{medal}</td>
                <td>{name}</td>
                <td class="time">{data['processing_time']:.2f}s</td>
                <td class="elements">{data['total_elements']}</td>
                <td>{data['table_count']}</td>
                <td>{efficiency:.2f}</td>
            </tr>
"""

html_report += """
        </table>
        
        <h2>📋 Prompt Details</h2>
"""

for name, data in all_results.items():
    if data['success']:
        html_report += f"""
        <div class="prompt-card">
            <h3>{name}</h3>
            <p><strong>Description:</strong> {data['prompt_info']['description']}</p>
            <p><strong>Difficulty:</strong> {data['prompt_info']['difficulty']}</p>
            <p><strong>Processing Time:</strong> <span class="time">{data['processing_time']:.2f}s</span></p>
            <p><strong>Elements Detected:</strong> <span class="elements">{data['total_elements']}</span></p>
            <p><strong>Tables:</strong> {data['table_count']}, <strong>Text:</strong> {data['text_count']}, <strong>Titles:</strong> {data['title_count']}</p>
            <p><strong>Output:</strong> {data['output_dir']}</p>
        </div>
"""

html_report += """
    </div>
</body>
</html>
"""

html_file = f"{BASE_OUTPUT_DIR}/analysis_report_{timestamp}.html"
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_report)

print(f"📄 HTML report saved: {html_file}")
print(f"   Open in browser: file:///{Path(html_file).absolute()}")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)
print(f"\nAll outputs saved in: {BASE_OUTPUT_DIR}/")
print("\nNext steps:")
print("  1. Review comparison images in each prompt folder")
print("  2. Check HTML report for detailed analysis")
print("  3. Choose best prompt for your use case")
print()