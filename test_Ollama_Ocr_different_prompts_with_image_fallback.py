"""
Prompt Analysis: Baseline vs Fallback-to-Image Strategy
Tests 6 prompts to compare standard extraction vs smart fallback.
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from DocumentParser import OllamaOCR
from DocumentParser.config import get_full_output_config, OCRConfig

print("="*80)
print("BASELINE vs FALLBACK-TO-IMAGE STRATEGY")
print("="*80)

# ========== CONFIGURE YOUR FILE HERE ==========
# YOUR_FILE = r"dont_send/02AC001(1)：下野部工場　機密区域管理要領_single_3.pdf"
YOUR_FILE = r"dont_send\shimonobe_file2_page6.pdf"
BASE_OUTPUT_DIR = "prompt_comparison_fallback2"
# ==============================================

# ========== PROMPTS TO TEST ==========
TEST_PROMPTS = {
    # ===== BASELINE (Standard Extraction) =====
    
    "1_table_focused": {
        "prompt": "<image>\n<|grounding|>Extract all text and tables from this document in markdown format. Include complete table structures with all headers and data rows.",
        "description": "Table-focused (baseline)",
        "type": "BASELINE",
        "difficulty": "Medium",
        "expected_speed": "Fast (2-3s)",
        "best_for": "Documents with clear tables"
    },
    
    "2_comprehensive": {
        "prompt": "<image>\n<|grounding|>Extract all text and tables from this document in markdown format. Include complete table structures with all headers and data rows. Preserve document layout and hierarchy.",
        "description": "Comprehensive (baseline)",
        "type": "BASELINE",
        "difficulty": "Medium-High",
        "expected_speed": "Fast (2-3s)",
        "best_for": "Complex documents"
    },
    
    # "3_japanese_focused": {
    #     "prompt": "<image>\n<|grounding|>この文書から全てのテキストと表を抽出してください。完全な表構造を含めてください。",
    #     "description": "Japanese (baseline)",
    #     "type": "BASELINE",
    #     "difficulty": "Medium",
    #     "expected_speed": "Fast (2-3s)",
    #     "best_for": "Japanese documents"
    # },
    
    # ===== FALLBACK (Smart Extraction) =====
    
    "4_table_fallback": {
        "prompt": "<image>\n<|grounding|>Extract all text and tables from this document. Include complete table structures. If any element's structure is unclear or ambiguous, mark it as an image instead of forcing interpretation.",
        "description": "Table with fallback",
        "type": "FALLBACK",
        "difficulty": "Medium",
        "expected_speed": "Fast (2-3s)",
        "best_for": "Complex/unclear tables"
    },
    
    "5_comprehensive_safe": {
        "prompt": "<image>\n<|grounding|>Extract all content from this document including tables and text. For complex or ambiguous structures that cannot be clearly parsed, mark them as images rather than guessing. Preserve what is clear, mark unclear as image.",
        "description": "Comprehensive with safe fallback",
        "type": "FALLBACK",
        "difficulty": "Medium-High",
        "expected_speed": "Fast (2-3s)",
        "best_for": "Mixed clarity documents"
    },
    
    # "6_japanese_smart": {
    #     "prompt": "<image>\n<|grounding|>この文書から全てのテキストと表を抽出してください。表の構造が不明確な場合は、画像として扱ってください。無理に解釈しないでください。",
    #     "description": "Japanese with smart fallback",
    #     "type": "FALLBACK",
    #     "difficulty": "Medium",
    #     "expected_speed": "Fast (2-3s)",
    #     "best_for": "Japanese manufacturing docs"
    # }
}
# ======================================

# Check file
file_path = Path(YOUR_FILE)
if not file_path.exists():
    print(f"\n❌ File not found: {YOUR_FILE}")
    sys.exit(1)

print(f"\n✓ Test file: {file_path.name}")
print(f"  Size: {file_path.stat().st_size:,} bytes")

print("\n📋 Testing Strategy:")
print("  BASELINE (3 prompts): Standard extraction")
print("  FALLBACK (3 prompts): Smart extraction with image fallback")
print("\n⚠️  Note: First prompt includes model loading time (~30s)")
print("   Subsequent prompts show true OCR speed (~2-3s)\n")

# Store results
all_results = {}
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Process each prompt
for prompt_name, prompt_info in TEST_PROMPTS.items():
    print("\n" + "="*80)
    print(f"🔬 TESTING: {prompt_name}")
    print("="*80)
    print(f"Type: {prompt_info['type']}")
    print(f"Description: {prompt_info['description']}")
    print(f"Expected: {prompt_info['expected_speed']}")
    print("-"*80)
    
    output_dir = f"{BASE_OUTPUT_DIR}/{prompt_name}_{timestamp}"
    
    try:
        output_config = get_full_output_config()
        ocr_config = OCRConfig(
            model_name="deepseek-ocr:3b",
            output_config=output_config,
            output_dir=output_dir
        )
        
        ocr = OllamaOCR(config=ocr_config)
        print(f"✓ OCR ready, output: {output_dir}")
        
        start_time = datetime.now()
        
        result = ocr.process(
            file_path=str(file_path),
            custom_prompt=prompt_info['prompt'],
            verbose=False
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        if result.success:
            # Analyze elements
            element_types = {}
            for page_result in result.page_results:
                for element in page_result.extraction_result.get_elements():
                    elem_type = element.element_type
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            # Count specific types
            table_count = element_types.get('table', 0)
            text_count = element_types.get('text', 0)
            image_count = element_types.get('image', 0)
            title_count = element_types.get('title', 0) + element_types.get('sub_title', 0)
            
            all_results[prompt_name] = {
                'success': True,
                'type': prompt_info['type'],
                'processing_time': processing_time,
                'total_elements': result.get_total_elements(),
                'element_breakdown': element_types,
                'table_count': table_count,
                'text_count': text_count,
                'image_count': image_count,
                'title_count': title_count,
                'output_dir': output_dir,
                'prompt_info': prompt_info
            }
            
            print(f"\n✅ SUCCESS")
            print(f"  ⏱️  Time: {processing_time:.2f}s")
            print(f"  📊 Elements: {result.get_total_elements()}")
            print(f"  📋 Tables: {table_count}")
            print(f"  🖼️  Images: {image_count}")
            print(f"\n  Breakdown:")
            for elem_type, count in sorted(element_types.items()):
                print(f"    {elem_type:15s}: {count:3d}")
        
        else:
            all_results[prompt_name] = {
                'success': False,
                'type': prompt_info['type'],
                'error': result.error_message,
                'processing_time': processing_time
            }
            print(f"\n❌ FAILED: {result.error_message}")
    
    except Exception as e:
        all_results[prompt_name] = {
            'success': False,
            'type': prompt_info['type'],
            'error': str(e),
            'processing_time': 0
        }
        print(f"\n❌ EXCEPTION: {str(e)}")

# Analysis
print("\n" + "="*80)
print("📊 COMPARATIVE ANALYSIS")
print("="*80)

successful = {k: v for k, v in all_results.items() if v['success']}

if successful:
    baseline = {k: v for k, v in successful.items() if v['type'] == 'BASELINE'}
    fallback = {k: v for k, v in successful.items() if v['type'] == 'FALLBACK'}
    
    print("\n" + "-"*80)
    print("BASELINE STRATEGY (Standard Extraction)")
    print("-"*80)
    print(f"{'Prompt':25s} {'Time':8s} {'Elements':10s} {'Tables':8s} {'Images':8s}")
    print("-"*80)
    
    for name, data in baseline.items():
        print(f"{name:25s} {data['processing_time']:6.2f}s {data['total_elements']:8d}   {data['table_count']:6d}  {data['image_count']:6d}")
    
    print("\n" + "-"*80)
    print("FALLBACK STRATEGY (Smart Extraction)")
    print("-"*80)
    print(f"{'Prompt':25s} {'Time':8s} {'Elements':10s} {'Tables':8s} {'Images':8s}")
    print("-"*80)
    
    for name, data in fallback.items():
        print(f"{name:25s} {data['processing_time']:6.2f}s {data['total_elements']:8d}   {data['table_count']:6d}  {data['image_count']:6d}")
    
    # Strategy comparison
    print("\n" + "="*80)
    print("🔍 STRATEGY COMPARISON")
    print("="*80)
    
    if baseline and fallback:
        avg_baseline_images = sum(d['image_count'] for d in baseline.values()) / len(baseline)
        avg_fallback_images = sum(d['image_count'] for d in fallback.values()) / len(fallback)
        
        avg_baseline_tables = sum(d['table_count'] for d in baseline.values()) / len(baseline)
        avg_fallback_tables = sum(d['table_count'] for d in fallback.values()) / len(fallback)
        
        print(f"\nAverage Images per Strategy:")
        print(f"  BASELINE: {avg_baseline_images:.1f} images")
        print(f"  FALLBACK: {avg_fallback_images:.1f} images")
        
        if avg_fallback_images > avg_baseline_images:
            print(f"  ✓ Fallback detected {avg_fallback_images - avg_baseline_images:.1f} more images")
            print(f"    → Strategy working! Marking unclear elements as images.")
        else:
            print(f"  → Similar image counts. Tables may be clear enough for parsing.")
        
        print(f"\nAverage Tables per Strategy:")
        print(f"  BASELINE: {avg_baseline_tables:.1f} tables")
        print(f"  FALLBACK: {avg_fallback_tables:.1f} tables")
        
        if avg_fallback_tables < avg_baseline_tables:
            print(f"  ✓ Fallback parsed {avg_baseline_tables - avg_fallback_tables:.1f} fewer tables")
            print(f"    → Correctly marking unclear tables as images!")
        
    # Best prompt
    print("\n" + "="*80)
    print("🏆 BEST PROMPTS")
    print("="*80)
    
    sorted_by_time = sorted(successful.items(), key=lambda x: x[1]['processing_time'])
    sorted_by_images = sorted(successful.items(), key=lambda x: x[1]['image_count'], reverse=True)
    sorted_by_tables = sorted(successful.items(), key=lambda x: x[1]['table_count'], reverse=True)
    
    print(f"\n⚡ Fastest: {sorted_by_time[0][0]}")
    print(f"   Time: {sorted_by_time[0][1]['processing_time']:.2f}s")
    
    print(f"\n🖼️  Most Images: {sorted_by_images[0][0]}")
    print(f"   Images: {sorted_by_images[0][1]['image_count']}")
    print(f"   (Good if using fallback strategy)")
    
    print(f"\n📋 Most Tables: {sorted_by_tables[0][0]}")
    print(f"   Tables: {sorted_by_tables[0][1]['table_count']}")
    
    # Recommendation
    print("\n" + "="*80)
    print("💡 RECOMMENDATION")
    print("="*80)
    
    # Check if fallback is working
    if avg_fallback_images > avg_baseline_images * 1.2:
        print("\n✓ Fallback strategy is working!")
        print("\nRECOMMENDATION: Use FALLBACK prompts")
        print("  Reason: Detecting more images = marking unclear elements safely")
        print(f"  Best: {sorted_by_images[0][0]}")
        print("\n  Benefits:")
        print("    • Prevents hallucination")
        print("    • Captures unclear tables as images")
        print("    • Can post-process images with LLM later")
    else:
        print("\n→ Tables appear clear enough for direct parsing")
        print("\nRECOMMENDATION: Use BASELINE prompts")
        print("  Reason: Direct table parsing working well")
        print(f"  Best: {sorted_by_tables[0][0]}")
        print("\n  Benefits:")
        print("    • More tables parsed directly")
        print("    • Less post-processing needed")

# Save JSON report
report_file = f"{BASE_OUTPUT_DIR}/comparison_report_{timestamp}.json"
Path(BASE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\n\n📄 JSON Report saved: {report_file}")

# Generate HTML Report
print("📄 Generating HTML report...")

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baseline vs Fallback Strategy - {timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .info-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .info-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        .info-card p {{
            color: #666;
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .strategy-section {{
            margin-bottom: 30px;
        }}
        
        .strategy-header {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-size: 1.3em;
            font-weight: bold;
        }}
        
        .baseline-header {{
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        .fallback-header {{
            background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f5f7ff;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .metric {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .metric-time {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .metric-elements {{
            background: #fff3e0;
            color: #f57c00;
        }}
        
        .metric-tables {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}
        
        .metric-images {{
            background: #e8f5e9;
            color: #388e3c;
        }}
        
        .comparison-box {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #667eea;
        }}
        
        .comparison-box h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
        
        .comparison-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px dashed #ccc;
        }}
        
        .comparison-item:last-child {{
            border-bottom: none;
        }}
        
        .comparison-label {{
            font-weight: 600;
            color: #555;
        }}
        
        .comparison-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .winner-badge {{
            display: inline-block;
            padding: 8px 20px;
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #333;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            margin: 10px 0;
        }}
        
        .recommendation {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .recommendation h3 {{
            font-size: 1.8em;
            margin-bottom: 15px;
        }}
        
        .recommendation ul {{
            list-style: none;
            margin-top: 15px;
        }}
        
        .recommendation li {{
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
        }}
        
        .recommendation li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            font-weight: bold;
            font-size: 1.2em;
        }}
        
        .prompt-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            transition: all 0.3s ease;
        }}
        
        .prompt-card:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            transform: translateY(-2px);
        }}
        
        .prompt-card h4 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.3em;
        }}
        
        .prompt-type {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .type-baseline {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .type-fallback {{
            background: #e8f5e9;
            color: #388e3c;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin: 15px 0;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .stat-label {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            margin-top: 40px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Baseline vs Fallback Strategy Analysis</h1>
            <p>Comparing Standard Extraction vs Smart Image Fallback</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Generated: {timestamp}</p>
        </div>
        
        <div class="content">
            <!-- Test Info -->
            <div class="section">
                <h2>📋 Test Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>Test File</h3>
                        <p style="font-size: 1em; word-break: break-word;">{file_path.name}</p>
                    </div>
                    <div class="info-card">
                        <h3>File Size</h3>
                        <p>{file_path.stat().st_size:,} bytes</p>
                    </div>
                    <div class="info-card">
                        <h3>Prompts Tested</h3>
                        <p>{len(TEST_PROMPTS)}</p>
                    </div>
                    <div class="info-card">
                        <h3>Successful Tests</h3>
                        <p>{len(successful)}</p>
                    </div>
                </div>
            </div>
"""

# Add baseline results
if baseline:
    html_content += """
            <!-- Baseline Results -->
            <div class="section">
                <div class="strategy-section">
                    <div class="strategy-header baseline-header">
                        🔵 BASELINE STRATEGY - Standard Extraction
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Prompt</th>
                                <th>Time</th>
                                <th>Elements</th>
                                <th>Tables</th>
                                <th>Images</th>
                                <th>Text</th>
                            </tr>
                        </thead>
                        <tbody>
"""
    
    for name, data in baseline.items():
        html_content += f"""
                            <tr>
                                <td><strong>{name}</strong><br><small style="color: #666;">{data['prompt_info']['description']}</small></td>
                                <td><span class="metric metric-time">{data['processing_time']:.2f}s</span></td>
                                <td><span class="metric metric-elements">{data['total_elements']}</span></td>
                                <td><span class="metric metric-tables">{data['table_count']}</span></td>
                                <td><span class="metric metric-images">{data['image_count']}</span></td>
                                <td><span class="metric">{data['text_count']}</span></td>
                            </tr>
"""
    
    html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
"""

# Add fallback results
if fallback:
    html_content += """
            <!-- Fallback Results -->
            <div class="section">
                <div class="strategy-section">
                    <div class="strategy-header fallback-header">
                        🟢 FALLBACK STRATEGY - Smart Image Fallback
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Prompt</th>
                                <th>Time</th>
                                <th>Elements</th>
                                <th>Tables</th>
                                <th>Images</th>
                                <th>Text</th>
                            </tr>
                        </thead>
                        <tbody>
"""
    
    for name, data in fallback.items():
        html_content += f"""
                            <tr>
                                <td><strong>{name}</strong><br><small style="color: #666;">{data['prompt_info']['description']}</small></td>
                                <td><span class="metric metric-time">{data['processing_time']:.2f}s</span></td>
                                <td><span class="metric metric-elements">{data['total_elements']}</span></td>
                                <td><span class="metric metric-tables">{data['table_count']}</span></td>
                                <td><span class="metric metric-images">{data['image_count']}</span></td>
                                <td><span class="metric">{data['text_count']}</span></td>
                            </tr>
"""
    
    html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
"""

# Add comparison
if baseline and fallback:
    avg_baseline_images = sum(d['image_count'] for d in baseline.values()) / len(baseline)
    avg_fallback_images = sum(d['image_count'] for d in fallback.values()) / len(fallback)
    avg_baseline_tables = sum(d['table_count'] for d in baseline.values()) / len(baseline)
    avg_fallback_tables = sum(d['table_count'] for d in fallback.values()) / len(fallback)
    avg_baseline_time = sum(d['processing_time'] for d in baseline.values()) / len(baseline)
    avg_fallback_time = sum(d['processing_time'] for d in fallback.values()) / len(fallback)
    
    html_content += f"""
            <!-- Strategy Comparison -->
            <div class="section">
                <h2>🔍 Strategy Comparison</h2>
                
                <div class="comparison-box">
                    <h3>Average Metrics</h3>
                    
                    <div class="comparison-item">
                        <span class="comparison-label">⏱️ Processing Time</span>
                        <div>
                            <span class="comparison-value">BASELINE: {avg_baseline_time:.2f}s</span>
                            <span style="margin: 0 10px;">vs</span>
                            <span class="comparison-value">FALLBACK: {avg_fallback_time:.2f}s</span>
                        </div>
                    </div>
                    
                    <div class="comparison-item">
                        <span class="comparison-label">🖼️ Images Detected</span>
                        <div>
                            <span class="comparison-value">BASELINE: {avg_baseline_images:.1f}</span>
                            <span style="margin: 0 10px;">vs</span>
                            <span class="comparison-value">FALLBACK: {avg_fallback_images:.1f}</span>
                        </div>
                    </div>
                    
                    <div class="comparison-item">
                        <span class="comparison-label">📋 Tables Detected</span>
                        <div>
                            <span class="comparison-value">BASELINE: {avg_baseline_tables:.1f}</span>
                            <span style="margin: 0 10px;">vs</span>
                            <span class="comparison-value">FALLBACK: {avg_fallback_tables:.1f}</span>
                        </div>
                    </div>
"""
    
    if avg_fallback_images > avg_baseline_images * 1.2:
        image_diff = avg_fallback_images - avg_baseline_images
        html_content += f"""
                    <div class="comparison-item">
                        <span class="comparison-label">📊 Analysis</span>
                        <span class="comparison-value" style="color: #43e97b;">
                            ✓ Fallback detected {image_diff:.1f} more images
                        </span>
                    </div>
                    <p style="margin-top: 15px; color: #666; font-style: italic;">
                        → Fallback strategy is working! Marking unclear elements as images for safer processing.
                    </p>
"""
    else:
        html_content += """
                    <div class="comparison-item">
                        <span class="comparison-label">📊 Analysis</span>
                        <span class="comparison-value" style="color: #2196f3;">
                            → Similar image counts detected
                        </span>
                    </div>
                    <p style="margin-top: 15px; color: #666; font-style: italic;">
                        → Tables appear clear enough for direct parsing. Baseline strategy sufficient.
                    </p>
"""
    
    html_content += """
                </div>
            </div>
"""

# Add best performers
if successful:
    sorted_by_time = sorted(successful.items(), key=lambda x: x[1]['processing_time'])
    sorted_by_images = sorted(successful.items(), key=lambda x: x[1]['image_count'], reverse=True)
    sorted_by_tables = sorted(successful.items(), key=lambda x: x[1]['table_count'], reverse=True)
    
    html_content += f"""
            <!-- Best Performers -->
            <div class="section">
                <h2>🏆 Best Performers</h2>
                
                <div class="info-grid">
                    <div class="info-card" style="border-left-color: #2196f3;">
                        <h3>⚡ Fastest</h3>
                        <p style="font-size: 1.1em;">{sorted_by_time[0][0]}</p>
                        <span class="metric metric-time">{sorted_by_time[0][1]['processing_time']:.2f}s</span>
                    </div>
                    
                    <div class="info-card" style="border-left-color: #388e3c;">
                        <h3>🖼️ Most Images</h3>
                        <p style="font-size: 1.1em;">{sorted_by_images[0][0]}</p>
                        <span class="metric metric-images">{sorted_by_images[0][1]['image_count']} images</span>
                    </div>
                    
                    <div class="info-card" style="border-left-color: #7b1fa2;">
                        <h3>📋 Most Tables</h3>
                        <p style="font-size: 1.1em;">{sorted_by_tables[0][0]}</p>
                        <span class="metric metric-tables">{sorted_by_tables[0][1]['table_count']} tables</span>
                    </div>
                    
                    <div class="info-card" style="border-left-color: #f57c00;">
                        <h3>📊 Most Elements</h3>
                        <p style="font-size: 1.1em;">{sorted(successful.items(), key=lambda x: x[1]['total_elements'], reverse=True)[0][0]}</p>
                        <span class="metric metric-elements">{sorted(successful.items(), key=lambda x: x[1]['total_elements'], reverse=True)[0][1]['total_elements']} elements</span>
                    </div>
                </div>
            </div>
"""

# Add recommendation
if baseline and fallback:
    if avg_fallback_images > avg_baseline_images * 1.2:
        recommended_prompt = sorted_by_images[0][0]
        recommendation_text = "Use FALLBACK prompts for your documents"
        reason = "Fallback strategy is detecting more images, meaning it's correctly marking unclear elements as images instead of hallucinating structure."
        benefits = [
            "Prevents hallucination on complex tables",
            "Captures unclear elements as images",
            "Allows post-processing with LLM",
            "More reliable for complex manufacturing documents"
        ]
    else:
        recommended_prompt = sorted_by_tables[0][0]
        recommendation_text = "Use BASELINE prompts for your documents"
        reason = "Your tables are clear enough for direct parsing. Baseline strategy is working well."
        benefits = [
            "Direct table parsing is accurate",
            "No post-processing needed",
            "Faster overall workflow",
            "Simpler processing pipeline"
        ]
    
    html_content += f"""
            <!-- Recommendation -->
            <div class="section">
                <div class="recommendation">
                    <h3>💡 RECOMMENDATION</h3>
                    <div class="winner-badge">🏆 {recommendation_text}</div>
                    <p style="margin: 20px 0; font-size: 1.1em;"><strong>Best Prompt:</strong> {recommended_prompt}</p>
                    <p style="margin-bottom: 15px;"><strong>Reason:</strong> {reason}</p>
                    <p><strong>Benefits:</strong></p>
                    <ul>
"""
    
    for benefit in benefits:
        html_content += f"                        <li>{benefit}</li>\n"
    
    html_content += """
                    </ul>
                </div>
            </div>
"""

# Add detailed prompt results
html_content += """
            <!-- Detailed Results -->
            <div class="section">
                <h2>📝 Detailed Prompt Results</h2>
"""

for name, data in successful.items():
    prompt_type = data['type']
    type_class = 'type-baseline' if prompt_type == 'BASELINE' else 'type-fallback'
    
    html_content += f"""
                <div class="prompt-card">
                    <span class="prompt-type {type_class}">{prompt_type}</span>
                    <h4>{name}</h4>
                    <p style="color: #666; margin-bottom: 15px;">{data['prompt_info']['description']}</p>
                    
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">Time</div>
                            <div class="stat-value">{data['processing_time']:.2f}s</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Elements</div>
                            <div class="stat-value">{data['total_elements']}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Tables</div>
                            <div class="stat-value">{data['table_count']}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Images</div>
                            <div class="stat-value">{data['image_count']}</div>
                        </div>
                    </div>
                    
                    <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                        <strong>Output:</strong> {data['output_dir']}
                    </p>
                </div>
"""

html_content += """
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Generated by DocumentParser OCR Analysis</strong></p>
            <p style="margin-top: 5px; font-size: 0.9em;">
                Test completed at {}</p>
            <p style="margin-top: 10px; font-size: 0.85em;">
                Review comparison images in output folders for visual verification
            </p>
        </div>
    </div>
</body>
</html>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Save HTML report
html_file = f"{BASE_OUTPUT_DIR}/comparison_report_{timestamp}.html"
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"📄 HTML Report saved: {html_file}")
print(f"   Open in browser: file:///{Path(html_file).absolute()}")

print("\n" + "="*80)
print("✅ COMPARISON COMPLETE!")
print("="*80)
print(f"\nAll outputs saved in: {BASE_OUTPUT_DIR}/")
print(f"\n📊 Reports generated:")
print(f"   • JSON: {report_file}")
print(f"   • HTML: {html_file}")
print("\n📁 Comparison folders:")
for name in successful.keys():
    print(f"   • {name}_{timestamp}/")
print("\n" + "="*80)
print("Next steps:")
print("="*80)
print("  1. Open HTML report in browser for visual analysis")
print("  2. Review comparison images in each prompt folder")
print("  3. Check which strategy captured tables better")
print("  4. Choose baseline or fallback based on results")
print("  5. Update your production prompts accordingly")
print()