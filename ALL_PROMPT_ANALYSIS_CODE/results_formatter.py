"""
Results Formatter
Generate outputs from test results: CSV, PDFs, analysis charts.

Outputs:
- CSV with all test results (190 rows)
- PDFs for each prompt (10 PDFs with 19 pages each)
- JSON with detailed data
- Analysis charts and recommendations
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from PIL import Image


# ========== CSV GENERATION ==========

def save_csv_summary(results_package, output_path):
    """
    Save test results to CSV file.
    
    Args:
        results_package (dict): Results from run_full_test()
        output_path (str): Path to save CSV
        
    Creates:
        CSV file with columns:
        - file, page, page_name, prompt_id, prompt_name
        - success, time, elements, tables, images, text
        - error, output_dir, comparison_image, timestamp
    """
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    results = results_package['results']
    
    # Define columns
    fieldnames = [
        'file',
        'page',
        'page_name',
        'prompt_id',
        'prompt_name',
        'success',
        'time_seconds',
        'elements_count',
        'tables_count',
        'images_count',
        'text_count',
        'error',
        'output_dir',
        'comparison_image',
        'timestamp'
    ]
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Write only the fields we want
            row = {field: result.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    print(f"  ✓ CSV saved: {output_path}")
    print(f"    Rows: {len(results)} (including header)")
    print(f"    Size: {output_path.stat().st_size:,} bytes")


# ========== JSON GENERATION ==========

def save_json_detailed(results_package, output_path):
    """
    Save detailed results to JSON file.
    
    Args:
        results_package (dict): Results from run_full_test()
        output_path (str): Path to save JSON
    """
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save with pretty printing
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results_package, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ JSON saved: {output_path}")
    print(f"    Size: {output_path.stat().st_size:,} bytes")


# ========== PDF GENERATION ==========

def create_comparison_pdf_for_prompt(prompt_id, prompt_name, results, output_dir):
    """
    Create single PDF with all comparison images for one prompt.
    
    Args:
        prompt_id (int): Prompt ID (1-10)
        prompt_name (str): Prompt name
        results (list): List of results for this prompt
        output_dir (str): Base output directory
        
    Creates:
        PDF file: output/prompt_XX_name/comparison_report.pdf
        Contains all comparison images for this prompt (one per page)
    """
    
    output_dir = Path(output_dir)
    prompt_dir = output_dir / f"prompt_{prompt_id:02d}_{prompt_name}"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = prompt_dir / "comparison_report.pdf"
    
    # Filter results for this prompt
    prompt_results = [r for r in results if r['prompt_id'] == prompt_id]
    
    if not prompt_results:
        print(f"  ⚠️  No results for prompt {prompt_id}")
        return None
    
    # Collect comparison images
    comparison_images = []
    
    for result in sorted(prompt_results, key=lambda x: (x['file'], x['page'])):
        if result['comparison_image'] and Path(result['comparison_image']).exists():
            comparison_images.append(result['comparison_image'])
    
    if not comparison_images:
        print(f"  ⚠️  No comparison images found for prompt {prompt_id}")
        return None
    
    # Create PDF from images
    try:
        pil_images = []
        
        for img_path in comparison_images:
            img = Image.open(img_path)
            
            # Convert to RGB (PDF requires RGB)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            pil_images.append(img)
        
        # Save as PDF
        if len(pil_images) == 1:
            pil_images[0].save(pdf_path, quality=95)
        else:
            pil_images[0].save(
                pdf_path,
                save_all=True,
                append_images=pil_images[1:],
                resolution=100.0,
                quality=95
            )
        
        size = pdf_path.stat().st_size
        print(f"  ✓ PDF created: {pdf_path.name}")
        print(f"    Pages: {len(pil_images)}, Size: {size:,} bytes")
        
        return pdf_path
    
    except Exception as e:
        print(f"  ❌ Error creating PDF for prompt {prompt_id}: {e}")
        return None


def create_all_comparison_pdfs(results_package, output_dir):
    """
    Create PDFs for all prompts.
    
    Args:
        results_package (dict): Results from run_full_test()
        output_dir (str): Base output directory
        
    Creates:
        One PDF per prompt (10 PDFs total)
        Each PDF contains all comparison images for that prompt
    """
    
    results = results_package['results']
    total_prompts = results_package['total_prompts']
    
    print(f"\n  Creating {total_prompts} comparison PDFs...")
    
    created_pdfs = []
    
    # Get unique prompts
    unique_prompts = {}
    for result in results:
        prompt_id = result['prompt_id']
        if prompt_id not in unique_prompts:
            unique_prompts[prompt_id] = result['prompt_name']
    
    # Create PDF for each prompt
    for prompt_id in sorted(unique_prompts.keys()):
        prompt_name = unique_prompts[prompt_id]
        
        print(f"\n  Prompt {prompt_id:2d}: {prompt_name}")
        
        pdf_path = create_comparison_pdf_for_prompt(
            prompt_id,
            prompt_name,
            results,
            output_dir
        )
        
        if pdf_path:
            created_pdfs.append(pdf_path)
    
    print(f"\n  ✓ Created {len(created_pdfs)} PDFs")
    
    return created_pdfs


# ========== ANALYSIS ==========

def generate_analysis_summary(results_package, output_dir):
    """
    Generate analysis summary and recommendations.
    
    Args:
        results_package (dict): Results from run_full_test()
        output_dir (str): Where to save analysis
        
    Creates:
        Text file with analysis and recommendations
    """
    
    output_dir = Path(output_dir)
    analysis_dir = output_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    
    results = results_package['results']
    summary = results_package['summary']
    
    # Calculate per-prompt statistics
    prompt_stats = {}
    
    for result in results:
        prompt_id = result['prompt_id']
        prompt_name = result['prompt_name']
        
        if prompt_id not in prompt_stats:
            prompt_stats[prompt_id] = {
                'name': prompt_name,
                'total': 0,
                'successful': 0,
                'timeouts': 0,
                'errors': 0,
                'total_time': 0.0,
                'total_elements': 0,
                'total_tables': 0,
            }
        
        stats = prompt_stats[prompt_id]
        stats['total'] += 1
        
        if result['success']:
            stats['successful'] += 1
            stats['total_time'] += result['time_seconds']
            stats['total_elements'] += result['elements_count']
            stats['total_tables'] += result['tables_count']
        elif result['error'] == 'timeout':
            stats['timeouts'] += 1
        else:
            stats['errors'] += 1
    
    # Calculate metrics
    for prompt_id, stats in prompt_stats.items():
        stats['success_rate'] = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
        stats['avg_time'] = (stats['total_time'] / stats['successful']) if stats['successful'] > 0 else 0
        stats['avg_elements'] = (stats['total_elements'] / stats['successful']) if stats['successful'] > 0 else 0
        stats['avg_tables'] = (stats['total_tables'] / stats['successful']) if stats['successful'] > 0 else 0
    
    # Find best prompts
    best_success = max(prompt_stats.items(), key=lambda x: x[1]['success_rate'])
    best_speed = min(
        [(pid, stats) for pid, stats in prompt_stats.items() if stats['successful'] > 0],
        key=lambda x: x[1]['avg_time'],
        default=(None, None)
    )
    best_tables = max(prompt_stats.items(), key=lambda x: x[1]['total_tables'])
    
    # Generate report
    report_path = analysis_dir / "analysis_report.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("PROMPT TESTING ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total tests: {results_package['total_tests']}\n")
        f.write(f"Duration: {results_package['duration_seconds']:.1f}s ({results_package['duration_seconds']/60:.1f} minutes)\n")
        f.write("\n" + "-"*80 + "\n")
        f.write("OVERALL SUMMARY\n")
        f.write("-"*80 + "\n\n")
        f.write(f"Successful tests: {summary['successful']}/{summary['total_tests']} ({summary['success_rate']:.1f}%)\n")
        f.write(f"Timeouts: {summary['timeouts']}\n")
        f.write(f"Errors: {summary['errors']}\n")
        f.write(f"Total elements found: {summary['total_elements']}\n")
        f.write(f"Total tables found: {summary['total_tables']}\n")
        f.write(f"Average time (successful): {summary['avg_time_success']:.1f}s\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("PROMPT PERFORMANCE COMPARISON\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"{'ID':3s} {'Prompt Name':30s} {'Success':8s} {'Avg Time':10s} {'Tables':8s} {'Timeouts':10s}\n")
        f.write("-"*80 + "\n")
        
        for prompt_id in sorted(prompt_stats.keys()):
            stats = prompt_stats[prompt_id]
            f.write(f"{prompt_id:2d}  {stats['name']:30s} ")
            f.write(f"{stats['success_rate']:6.1f}%  ")
            f.write(f"{stats['avg_time']:8.1f}s  ")
            f.write(f"{stats['total_tables']:6d}  ")
            f.write(f"{stats['timeouts']:8d}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("="*80 + "\n\n")
        
        f.write("🏆 BEST FOR SUCCESS RATE:\n")
        f.write(f"   Prompt {best_success[0]}: {best_success[1]['name']}\n")
        f.write(f"   Success rate: {best_success[1]['success_rate']:.1f}%\n")
        f.write(f"   ({best_success[1]['successful']}/{best_success[1]['total']} pages)\n\n")
        
        if best_speed[0]:
            f.write("⚡ BEST FOR SPEED:\n")
            f.write(f"   Prompt {best_speed[0]}: {best_speed[1]['name']}\n")
            f.write(f"   Average time: {best_speed[1]['avg_time']:.1f}s\n\n")
        
        f.write("📋 BEST FOR TABLE DETECTION:\n")
        f.write(f"   Prompt {best_tables[0]}: {best_tables[1]['name']}\n")
        f.write(f"   Total tables: {best_tables[1]['total_tables']}\n")
        f.write(f"   Average per page: {best_tables[1]['avg_tables']:.1f}\n\n")
        
        # Problem pages
        f.write("\n" + "="*80 + "\n")
        f.write("PROBLEM PAGES (Failed with all prompts)\n")
        f.write("="*80 + "\n\n")
        
        # Group by page
        page_results = {}
        for result in results:
            page_key = (result['file'], result['page'])
            if page_key not in page_results:
                page_results[page_key] = []
            page_results[page_key].append(result)
        
        problem_pages = []
        for page_key, page_tests in page_results.items():
            if all(not r['success'] for r in page_tests):
                problem_pages.append(page_key)
        
        if problem_pages:
            for file, page in problem_pages:
                f.write(f"  • {file} - Page {page}\n")
        else:
            f.write("  None! All pages successful with at least one prompt.\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("NEXT STEPS\n")
        f.write("="*80 + "\n\n")
        
        if best_success[1]['success_rate'] >= 90:
            f.write("✅ EXCELLENT RESULTS!\n")
            f.write(f"   Use: {best_success[1]['name']}\n")
            f.write("   This prompt works well for your documents.\n")
        elif best_success[1]['success_rate'] >= 70:
            f.write("⚠️  GOOD RESULTS, ROOM FOR IMPROVEMENT\n")
            f.write(f"   Primary: {best_success[1]['name']}\n")
            f.write("   Consider prompt refinement or hybrid approach.\n")
        else:
            f.write("❌ NEEDS IMPROVEMENT\n")
            f.write("   Consider:\n")
            f.write("   1. Trying different model (GPT-4 Vision, Claude)\n")
            f.write("   2. Creating document-specific prompts\n")
            f.write("   3. Manual review of problem pages\n")
        
        f.write("\n" + "="*80 + "\n")
    
    print(f"  ✓ Analysis saved: {report_path}")
    
    return report_path


# ========== MASTER FORMATTER ==========

def format_all_results(results_package, output_dir):
    """
    Generate all output formats.
    
    Args:
        results_package (dict): Results from run_full_test()
        output_dir (str): Base output directory
        
    Creates:
        - CSV file
        - JSON file
        - Comparison PDFs (one per prompt)
        - Analysis report
    """
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print("FORMATTING RESULTS")
    print("="*80)
    
    # 1. CSV
    print("\n[1/4] Generating CSV...")
    csv_path = output_dir / "results_summary.csv"
    save_csv_summary(results_package, csv_path)
    
    # 2. JSON
    print("\n[2/4] Generating JSON...")
    json_path = output_dir / "results_detailed.json"
    save_json_detailed(results_package, json_path)
    
    # 3. PDFs
    print("\n[3/4] Generating comparison PDFs...")
    pdf_paths = create_all_comparison_pdfs(results_package, output_dir)
    
    # 4. Analysis
    print("\n[4/4] Generating analysis...")
    analysis_path = generate_analysis_summary(results_package, output_dir)
    
    print("\n" + "="*80)
    print("FORMATTING COMPLETE")
    print("="*80)
    print(f"\nOutputs saved in: {output_dir}")
    print(f"\nFiles created:")
    print(f"  • CSV: {csv_path.name}")
    print(f"  • JSON: {json_path.name}")
    print(f"  • PDFs: {len(pdf_paths)} files")
    print(f"  • Analysis: analysis/analysis_report.txt")
    print("="*80)
    
    return {
        'csv': csv_path,
        'json': json_path,
        'pdfs': pdf_paths,
        'analysis': analysis_path
    }


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*80)
    print("RESULTS FORMATTER - STANDALONE TEST")
    print("="*80)
    
    # Create dummy results for testing
    dummy_results = {
        'total_tests': 6,
        'total_files': 1,
        'total_pages': 2,
        'total_prompts': 3,
        'results': [
            {
                'file': 'test.pdf',
                'page': 1,
                'page_name': 'page_001',
                'prompt_id': 1,
                'prompt_name': 'japanese_simple',
                'success': True,
                'time_seconds': 8.5,
                'elements_count': 7,
                'tables_count': 2,
                'images_count': 1,
                'text_count': 4,
                'error': None,
                'output_dir': 'test_output',
                'comparison_image': None,
                'timestamp': datetime.now().isoformat()
            },
            # Add more dummy results...
        ],
        'summary': {
            'total_tests': 6,
            'successful': 4,
            'timeouts': 1,
            'errors': 1,
            'success_rate': 66.7,
            'avg_time_success': 10.5,
            'total_elements': 28,
            'total_tables': 8,
        },
        'start_time': datetime.now().isoformat(),
        'end_time': datetime.now().isoformat(),
        'duration_seconds': 95.5
    }
    
    # Test CSV generation
    print("\nTesting CSV generation...")
    save_csv_summary(dummy_results, "test_output/test_results.csv")
    
    # Test JSON generation
    print("\nTesting JSON generation...")
    save_json_detailed(dummy_results, "test_output/test_results.json")
    
    # Test analysis generation
    print("\nTesting analysis generation...")
    generate_analysis_summary(dummy_results, "test_output")
    
    print("\n✓ Results formatter ready!")
    print("\nUsage:")
    print("  from results_formatter import format_all_results")
    print("  format_all_results(results_package, output_dir)")
    print()