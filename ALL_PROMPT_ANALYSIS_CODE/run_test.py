"""
Run Prompt Testing
Main entry point for testing framework.

This script:
1. Loads prompts from prompts_config.py
2. Runs tests on all PDF files
3. Generates all outputs (CSV, PDFs, analysis)
4. Provides summary and recommendations

Usage:
    python run_test.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from prompts_config import get_all_prompts, print_prompts_summary
from test_engine import run_full_test
from results_formatter import format_all_results


# ========== CONFIGURATION ==========

# YOUR FILES TO TEST
PDF_FILES = [
    "file1.pdf",
    # "file3.pdf",
]

# OUTPUT DIRECTORY
OUTPUT_DIR = "qwen3vl_file1_output"

# TIMEOUT PER TEST (seconds)
TIMEOUT = 60

# VERBOSE OUTPUT
VERBOSE = True


# ========== HELPER FUNCTIONS ==========

def check_files_exist(pdf_files):
    """
    Check if all PDF files exist.
    
    Args:
        pdf_files (list): List of PDF file paths
        
    Returns:
        tuple: (all_exist, missing_files)
    """
    missing = []
    
    for pdf_file in pdf_files:
        if not Path(pdf_file).exists():
            missing.append(pdf_file)
    
    return (len(missing) == 0, missing)


def print_configuration(pdf_files, prompts, timeout, output_dir):
    """Print test configuration."""
    
    print("="*80)
    print("TEST CONFIGURATION")
    print("="*80)
    
    print(f"\n📁 PDF Files: {len(pdf_files)}")
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = Path(pdf_file)
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            print(f"  {i}. {pdf_path.name:40s} ({size:,} bytes) ✓")
        else:
            print(f"  {i}. {pdf_path.name:40s} ❌ NOT FOUND")
    
    print(f"\n📋 Prompts: {len(prompts)}")
    for prompt in prompts[:3]:  # Show first 3
        print(f"  {prompt['id']:2d}. {prompt['name']:30s} - {prompt['description']}")
    if len(prompts) > 3:
        print(f"  ... and {len(prompts) - 3} more")
    
    print(f"\n⚙️  Settings:")
    print(f"  Timeout per test: {timeout}s")
    print(f"  Output directory: {output_dir}")
    print(f"  Verbose output: {VERBOSE}")
    
    # Calculate totals
    from test_engine import count_pdf_pages
    total_pages = sum(count_pdf_pages(f) for f in pdf_files if Path(f).exists())
    total_tests = total_pages * len(prompts)
    
    print(f"\n📊 Expected:")
    print(f"  Total pages: {total_pages}")
    print(f"  Total tests: {total_tests} ({total_pages} pages × {len(prompts)} prompts)")
    
    # Time estimates
    min_time = total_tests * 5 / 60  # Best case: 5s per test
    max_time = total_tests * timeout / 60  # Worst case: timeout every test
    avg_time = total_tests * 15 / 60  # Realistic: 15s average
    
    print(f"  Estimated time:")
    print(f"    Best case:  {min_time:6.1f} minutes ({total_tests * 5:,}s)")
    print(f"    Realistic:  {avg_time:6.1f} minutes ({total_tests * 15:,}s)")
    print(f"    Worst case: {max_time:6.1f} minutes ({total_tests * timeout:,}s)")
    
    print("="*80)


def print_final_summary(results_package, output_files):
    """Print final summary after test completion."""
    
    summary = results_package['summary']
    
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    print(f"\n⏱️  Duration: {results_package['duration_seconds']:.1f}s ({results_package['duration_seconds']/60:.1f} minutes)")
    
    print(f"\n📊 Results:")
    print(f"  Total tests: {summary['total_tests']}")
    print(f"  Successful: {summary['successful']} ({summary['success_rate']:.1f}%)")
    print(f"  Timeouts: {summary['timeouts']}")
    print(f"  Errors: {summary['errors']}")
    
    print(f"\n📈 Findings:")
    print(f"  Total elements: {summary['total_elements']}")
    print(f"  Total tables: {summary['total_tables']}")
    print(f"  Avg time (success): {summary['avg_time_success']:.1f}s")
    
    print(f"\n📁 Output Files:")
    print(f"  CSV: {output_files['csv'].name}")
    print(f"  JSON: {output_files['json'].name}")
    print(f"  PDFs: {len(output_files['pdfs'])} files")
    print(f"  Analysis: {output_files['analysis'].relative_to(Path(OUTPUT_DIR))}")
    
    print(f"\n📂 Output Directory: {Path(OUTPUT_DIR).absolute()}")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    
    print("\n1. Review CSV in Excel:")
    print(f"   Open: {output_files['csv']}")
    print("   Create pivot table to analyze prompts")
    
    print("\n2. Review PDFs visually:")
    print(f"   Location: {Path(OUTPUT_DIR)}/prompt_XX_*/comparison_report.pdf")
    print("   Compare side-by-side to see which prompt works best")
    
    print("\n3. Read analysis report:")
    print(f"   Open: {output_files['analysis']}")
    print("   See recommendations and best prompts")
    
    print("\n4. Choose your production prompt:")
    print("   Based on analysis, select the best prompt for your use case")
    
    print("\n" + "="*80)


# ========== MAIN FUNCTION ==========

def main():
    """Main execution function."""
    
    print("\n")
    print("█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  PROMPT TESTING FRAMEWORK".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    print()
    
    start_time = datetime.now()
    
    # ========== STEP 1: LOAD PROMPTS ==========
    
    print("\n[STEP 1/5] Loading prompts...")
    print("-"*80)
    
    prompts = get_all_prompts()
    print(f"✓ Loaded {len(prompts)} prompts")
    
    if VERBOSE:
        print("\nPrompt summary:")
        print_prompts_summary()
    
    # ========== STEP 2: VALIDATE FILES ==========
    
    print("\n[STEP 2/5] Validating input files...")
    print("-"*80)
    
    all_exist, missing = check_files_exist(PDF_FILES)
    
    if not all_exist:
        print("\n❌ ERROR: Missing PDF files!")
        for missing_file in missing:
            print(f"  ✗ {missing_file}")
        print("\nPlease update PDF_FILES in run_test.py with correct paths.")
        print("Current configuration:")
        print(f"  PDF_FILES = {PDF_FILES}")
        sys.exit(1)
    
    print(f"✓ All {len(PDF_FILES)} files found")
    
    # Print configuration
    print_configuration(PDF_FILES, prompts, TIMEOUT, OUTPUT_DIR)
    
    # ========== STEP 3: CONFIRMATION ==========
    
    print("\n[STEP 3/5] Ready to start testing")
    print("-"*80)
    
    # Calculate totals for confirmation
    from test_engine import count_pdf_pages
    total_pages = sum(count_pdf_pages(f) for f in PDF_FILES)
    total_tests = total_pages * len(prompts)
    
    print(f"\nThis will run {total_tests} tests ({total_pages} pages × {len(prompts)} prompts)")
    print(f"Estimated time: {total_tests * 15 / 60:.1f} minutes")
    
    # Auto-start or wait for confirmation
    AUTO_START = True  # Set to False to require confirmation
    
    if not AUTO_START:
        response = input("\nPress ENTER to start, or Ctrl+C to cancel: ")
    else:
        print("\nStarting in 3 seconds... (Ctrl+C to cancel)")
        import time
        try:
            for i in range(3, 0, -1):
                print(f"  {i}...")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user")
            sys.exit(0)
    
    # ========== STEP 4: RUN TESTS ==========
    
    print("\n[STEP 4/5] Running tests...")
    print("="*80)
    
    try:
        results_package = run_full_test(
            pdf_files=PDF_FILES,
            prompts=prompts,
            output_base_dir=OUTPUT_DIR,
            timeout=TIMEOUT,
            verbose=VERBOSE
        )
    
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user")
        print("Partial results may be available in output directory")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ========== STEP 5: GENERATE OUTPUTS ==========
    
    print("\n[STEP 5/5] Generating outputs...")
    print("="*80)
    
    try:
        output_files = format_all_results(results_package, OUTPUT_DIR)
    
    except Exception as e:
        print(f"\n\n❌ ERROR during output generation: {e}")
        import traceback
        traceback.print_exc()
        print("\nTest results are available but output formatting failed")
        sys.exit(1)
    
    # ========== FINAL SUMMARY ==========
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    print_final_summary(results_package, output_files)
    
    print(f"\n⏰ Total execution time: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print(f"   Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Ended:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n✅ ALL DONE!")
    print("\n" + "█"*80 + "\n")


# ========== ENTRY POINT ==========

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)