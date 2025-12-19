"""
Test OCR System - Batch Processing
Process multiple documents and generate detailed reports.
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
print("BATCH PROCESSING TEST")
print("="*80)

# ========== CONFIGURE YOUR FILES HERE ==========
BATCH_FILES = [
    # r"test_files\02AC001：下野部工場　機密区域管理要領\02AC001(1)：下野部工場　機密区域管理要領.pdf",
    # r"dont_send\test_files\21AC001：電気事業法　下野部工場保安規程\21AC001(2)：電気事業法　下野部工場保安規程.pdf",
    r"dont_send\M1-AM-STB3-25001 (1).pdf",
    r"dont_send\02AC001(1)：下野部工場　機密区域管理要領.pdf"
    # Add more files here
]

OUTPUT_DIR = "batch_output"
GENERATE_REPORT = True  # Create HTML report
# ==============================================

# Validate files
print(f"\n📁 Validating {len(BATCH_FILES)} files...")
print("-"*80)

valid_files = []
invalid_files = []

for file_path_str in BATCH_FILES:
    file_path = Path(file_path_str)
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"  ✓ {file_path.name}")
        print(f"    Size: {size:,} bytes")
        valid_files.append(file_path)
    else:
        print(f"  ✗ {file_path_str} - NOT FOUND")
        invalid_files.append(file_path_str)

if not valid_files:
    print("\n❌ No valid files found!")
    print("Please update BATCH_FILES in the script.")
    sys.exit(1)

if invalid_files:
    print(f"\n⚠ Warning: {len(invalid_files)} file(s) not found and will be skipped")

print(f"\n✓ Found {len(valid_files)} valid file(s) to process")

# Create OCR instance
print("\n" + "-"*80)
print("Creating OllamaOCR instance...")
print("-"*80)

try:
    # Use full output config
    output_config = get_full_output_config()
    
    # Create OCR config
    ocr_config = OCRConfig(
        model_name="deepseek-ocr:3b",
        output_config=output_config,
        output_dir=OUTPUT_DIR
    )
    
    # Create OCR instance
    ocr = OllamaOCR(config=ocr_config)
    
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

# Process documents
print("\n" + "="*80)
print("BATCH PROCESSING")
print("="*80)
print(f"Processing {len(valid_files)} document(s)...\n")

batch_start_time = datetime.now()
all_results = []

for idx, file_path in enumerate(valid_files, 1):
    print("="*80)
    print(f"[{idx}/{len(valid_files)}] Processing: {file_path.name}")
    print("="*80)
    
    try:
        result = ocr.process(
            file_path=str(file_path),
            verbose=True
        )
        
        all_results.append({
            'file_path': str(file_path),
            'file_name': file_path.name,
            'result': result,
            'success': result.success
        })
        
        if result.success:
            print(f"\n✓ Success: {file_path.name}")
            print(f"  Pages: {result.page_count}")
            print(f"  Elements: {result.get_total_elements()}")
            print(f"  Time: {result.total_processing_time:.2f}s")
        else:
            print(f"\n✗ Failed: {file_path.name}")
            print(f"  Error: {result.error_message}")
    
    except Exception as e:
        print(f"\n✗ Exception while processing {file_path.name}")
        print(f"  Error: {str(e)}")
        
        # Create a failed result
        all_results.append({
            'file_path': str(file_path),
            'file_name': file_path.name,
            'result': None,
            'success': False,
            'error': str(e)
        })
    
    print()  # Add spacing between files

batch_end_time = datetime.now()
total_batch_time = (batch_end_time - batch_start_time).total_seconds()

# Generate summary
print("\n" + "="*80)
print("BATCH PROCESSING SUMMARY")
print("="*80)

successful_results = [r for r in all_results if r['success']]
failed_results = [r for r in all_results if not r['success']]

print(f"\nTotal files processed: {len(all_results)}")
print(f"Successful: {len(successful_results)}")
print(f"Failed: {len(failed_results)}")
print(f"Total batch time: {total_batch_time:.2f}s")

if successful_results:
    total_pages = sum(r['result'].page_count for r in successful_results)
    total_elements = sum(r['result'].get_total_elements() for r in successful_results)
    avg_time = sum(r['result'].total_processing_time for r in successful_results) / len(successful_results)
    
    print(f"\nTotal pages processed: {total_pages}")
    print(f"Total elements extracted: {total_elements}")
    print(f"Average processing time: {avg_time:.2f}s per document")

# Show successful files
if successful_results:
    print("\n" + "-"*80)
    print("✓ Successful Files:")
    print("-"*80)
    for r in successful_results:
        result = r['result']
        print(f"\n  {r['file_name']}")
        print(f"    Pages: {result.page_count}")
        print(f"    Elements: {result.get_total_elements()}")
        print(f"    Time: {result.total_processing_time:.2f}s")
        print(f"    Output: {result.output_dir}")

# Show failed files
if failed_results:
    print("\n" + "-"*80)
    print("✗ Failed Files:")
    print("-"*80)
    for r in failed_results:
        print(f"\n  {r['file_name']}")
        if r.get('result') and r['result']:
            print(f"    Error: {r['result'].error_message}")
        elif r.get('error'):
            print(f"    Error: {r['error']}")

# Element statistics across all documents
if successful_results:
    print("\n" + "-"*80)
    print("Element Statistics (All Documents):")
    print("-"*80)
    
    all_element_types = {}
    for r in successful_results:
        for page_result in r['result'].page_results:
            for element in page_result.extraction_result.get_elements():
                elem_type = element.element_type
                all_element_types[elem_type] = all_element_types.get(elem_type, 0) + 1
    
    for elem_type, count in sorted(all_element_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {elem_type:15s}: {count:4d}")

# Generate HTML report
if GENERATE_REPORT and successful_results:
    print("\n" + "-"*80)
    print("Generating HTML Report...")
    print("-"*80)
    
    report_path = Path(OUTPUT_DIR) / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch Processing Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .document {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .document.success {{
            border-left: 4px solid #4caf50;
        }}
        .document.failed {{
            border-left: 4px solid #f44336;
        }}
        .document h2 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        .document .status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .document .status.success {{
            background-color: #4caf50;
            color: white;
        }}
        .document .status.failed {{
            background-color: #f44336;
            color: white;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }}
        .stat {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        .elements {{
            margin-top: 15px;
        }}
        .elements h3 {{
            font-size: 14px;
            color: #666;
            margin: 0 0 10px 0;
        }}
        .element-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .element-badge {{
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .output-link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 15px;
            background-color: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
        }}
        .output-link:hover {{
            background-color: #5568d3;
        }}
        .error-message {{
            background-color: #ffebee;
            color: #c62828;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 Batch OCR Processing Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Model: {ocr.config.model_name}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>Total Files</h3>
            <div class="value">{len(all_results)}</div>
        </div>
        <div class="summary-card">
            <h3>Successful</h3>
            <div class="value" style="color: #4caf50;">{len(successful_results)}</div>
        </div>
        <div class="summary-card">
            <h3>Failed</h3>
            <div class="value" style="color: #f44336;">{len(failed_results)}</div>
        </div>
        <div class="summary-card">
            <h3>Total Pages</h3>
            <div class="value">{sum(r['result'].page_count for r in successful_results) if successful_results else 0}</div>
        </div>
        <div class="summary-card">
            <h3>Total Elements</h3>
            <div class="value">{sum(r['result'].get_total_elements() for r in successful_results) if successful_results else 0}</div>
        </div>
        <div class="summary-card">
            <h3>Batch Time</h3>
            <div class="value" style="font-size: 24px;">{total_batch_time:.1f}s</div>
        </div>
    </div>
"""
    
    # Add individual document results
    for r in all_results:
        status_class = "success" if r['success'] else "failed"
        status_text = "SUCCESS" if r['success'] else "FAILED"
        
        html_content += f"""
    <div class="document {status_class}">
        <h2>{r['file_name']}</h2>
        <span class="status {status_class}">{status_text}</span>
"""
        
        if r['success']:
            result = r['result']
            
            # Stats
            html_content += f"""
        <div class="stats">
            <div class="stat">
                <div class="stat-label">Pages</div>
                <div class="stat-value">{result.page_count}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Elements</div>
                <div class="stat-value">{result.get_total_elements()}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Processing Time</div>
                <div class="stat-value">{result.total_processing_time:.2f}s</div>
            </div>
        </div>
"""
            
            # Element breakdown
            element_types = {}
            for page_result in result.page_results:
                for element in page_result.extraction_result.get_elements():
                    elem_type = element.element_type
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            if element_types:
                html_content += """
        <div class="elements">
            <h3>Element Types:</h3>
            <div class="element-list">
"""
                for elem_type, count in sorted(element_types.items()):
                    html_content += f"""
                <span class="element-badge">{elem_type}: {count}</span>
"""
                html_content += """
            </div>
        </div>
"""
            
            # Output link
            output_dir_abs = Path(result.output_dir).absolute()
            html_content += f"""
        <a href="file:///{output_dir_abs}" class="output-link">📁 Open Output Directory</a>
"""
        
        else:
            # Show error
            error_msg = r.get('error', r.get('result', {}).error_message if r.get('result') else 'Unknown error')
            html_content += f"""
        <div class="error-message">
            <strong>Error:</strong> {error_msg}
        </div>
"""
        
        html_content += """
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    # Save HTML report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML report generated: {report_path}")
    print(f"  Open in browser: file:///{report_path.absolute()}")

# Generate JSON report
json_report_path = Path(OUTPUT_DIR) / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

json_data = {
    'batch_info': {
        'start_time': batch_start_time.isoformat(),
        'end_time': batch_end_time.isoformat(),
        'total_time_seconds': total_batch_time,
        'model': ocr.config.model_name,
        'total_files': len(all_results),
        'successful_files': len(successful_results),
        'failed_files': len(failed_results)
    },
    'results': []
}

for r in all_results:
    if r['success']:
        result = r['result']
        element_types = {}
        for page_result in result.page_results:
            for element in page_result.extraction_result.get_elements():
                elem_type = element.element_type
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        json_data['results'].append({
            'file_name': r['file_name'],
            'file_path': r['file_path'],
            'success': True,
            'page_count': result.page_count,
            'total_elements': result.get_total_elements(),
            'element_types': element_types,
            'processing_time': result.total_processing_time,
            'output_dir': result.output_dir
        })
    else:
        json_data['results'].append({
            'file_name': r['file_name'],
            'file_path': r['file_path'],
            'success': False,
            'error': r.get('error', r.get('result', {}).error_message if r.get('result') else 'Unknown error')
        })

with open(json_report_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)

print(f"✓ JSON report generated: {json_report_path}")

# Final summary
print("\n" + "="*80)
print("🎉 BATCH PROCESSING COMPLETE!")
print("="*80)
print(f"\nOutput directory: {Path(OUTPUT_DIR).absolute()}")
print(f"HTML Report: {report_path if GENERATE_REPORT and successful_results else 'Not generated'}")
print(f"JSON Report: {json_report_path}")
print()