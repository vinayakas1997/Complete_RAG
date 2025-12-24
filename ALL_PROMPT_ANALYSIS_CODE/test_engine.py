"""
Test Engine
Main testing logic for running OCR tests with timeout handling.

Handles:
- Single page testing
- Timeout management
- Result collection
- Progress tracking
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Import your OCR system
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from DocumentParser import OllamaOCR
    from DocumentParser.config import get_full_output_config, OCRConfig
except ImportError:
    print("⚠️  Warning: Could not import DocumentParser")
    print("   Make sure DocumentParser is in parent directory")


# ========== TIMEOUT HANDLER (Windows-compatible) ==========

import threading

class TimeoutError(Exception):
    """Custom timeout exception."""
    pass


def run_with_timeout(func, args=(), kwargs=None, timeout=30):
    """
    Run function with timeout (Windows-compatible).
    
    Args:
        func: Function to run
        args: Function arguments
        kwargs: Function keyword arguments
        timeout: Timeout in seconds
        
    Returns:
        Function result
        
    Raises:
        TimeoutError: If function takes longer than timeout
    """
    if kwargs is None:
        kwargs = {}
    
    result = [None]
    exception = [None]
    
    def worker():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        # Thread is still running - timeout occurred
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]


# ========== SINGLE PAGE TESTING ==========

def extract_single_page(pdf_path, page_number, output_dir):
    """
    Extract a single page from PDF as image.
    
    Args:
        pdf_path: Path to PDF file
        page_number: Page number (1-indexed)
        output_dir: Where to save extracted page
        
    Returns:
        Path to extracted page image
    """
    from pdf2image import convert_from_path
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract single page
    images = convert_from_path(
        pdf_path,
        first_page=page_number,
        last_page=page_number
    )
    
    if images:
        page_path = output_dir / f"page_{page_number:03d}.png"
        images[0].save(page_path, 'PNG')
        return page_path
    
    return None


def count_pdf_pages(pdf_path):
    """
    Count pages in PDF.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        int: Number of pages
    """
    from pypdf import PdfReader
    
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception as e:
        print(f"Error counting pages in {pdf_path}: {e}")
        return 0


def test_single_page(pdf_file, page_num, prompt_config, output_base_dir, timeout=30):
    """
    Test single page with single prompt.
    
    Args:
        pdf_file (str): Path to PDF file
        page_num (int): Page number (1-indexed)
        prompt_config (dict): Prompt configuration from prompts_config.py
        output_base_dir (str): Base output directory
        timeout (int): Timeout in seconds
        
    Returns:
        dict: Test result with success, time, elements, etc.
    """
    
    result = {
        'file': Path(pdf_file).name,
        'page': page_num,
        'page_name': f"page_{page_num:03d}",
        'prompt_id': prompt_config['id'],
        'prompt_name': prompt_config['name'],
        'prompt_text': prompt_config['prompt'],
        'success': False,
        'time_seconds': 0.0,
        'elements_count': 0,
        'tables_count': 0,
        'images_count': 0,
        'text_count': 0,
        'output_dir': None,
        'comparison_image': None,
        'error': None,
        'timestamp': datetime.now().isoformat()
    }
    
    # Create output directory
    file_stem = Path(pdf_file).stem
    output_dir = Path(output_base_dir) / f"prompt_{prompt_config['id']:02d}_{prompt_config['name']}" / file_stem / f"page_{page_num:03d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    result['output_dir'] = str(output_dir)
    
    start_time = time.time()
    
    try:
        # Extract page as image (for single page processing)
        temp_dir = output_dir / "temp"
        page_image = extract_single_page(pdf_file, page_num, temp_dir)
        
        if not page_image:
            result['error'] = 'page_extraction_failed'
            return result
        
        # Setup OCR
        output_config = get_full_output_config()
        # ocr_config = OCRConfig(
        #     model_name="deepseek-ocr:3b",
        #     output_config=output_config,
        #     output_dir=str(output_dir)
        # )
        ocr_config = OCRConfig(
        model_name="qwen3-vl:latest",  # ← NEW MODEL
        output_config=output_config,
        output_dir=str(output_dir),
        use_grounding=False
        )
        ocr = OllamaOCR(config=ocr_config)
        
        # Define OCR function to run with timeout
        def run_ocr():
            return ocr.process(
                file_path=str(page_image),
                custom_prompt=prompt_config['prompt'],
                verbose=False
            )
        
        # Run OCR with timeout (Windows-compatible)
        ocr_result = run_with_timeout(run_ocr, timeout=timeout)
        
        # Calculate time
        elapsed = time.time() - start_time
        result['time_seconds'] = round(elapsed, 2)
        
        # Check success
        if ocr_result.success:
            result['success'] = True
            
            # Count elements
            result['elements_count'] = ocr_result.get_total_elements()
            
            # Count by type
            element_types = {}
            for page_result in ocr_result.page_results:
                for element in page_result.extraction_result.get_elements():
                    elem_type = element.element_type
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            result['tables_count'] = element_types.get('table', 0)
            result['images_count'] = element_types.get('image', 0)
            result['text_count'] = element_types.get('text', 0)
            
            # Find comparison image
            comparison_images = list(output_dir.glob("**/page_001_comparison.png"))
            if comparison_images:
                result['comparison_image'] = str(comparison_images[0])
        
        else:
            result['error'] = ocr_result.error_message or 'ocr_failed'
    
    except TimeoutError:
        elapsed = time.time() - start_time
        result['time_seconds'] = round(elapsed, 2)
        result['error'] = 'timeout'
    
    except ConnectionError as e:
        elapsed = time.time() - start_time
        result['time_seconds'] = round(elapsed, 2)
        result['error'] = f'connection_error: {str(e)}'
    
    except Exception as e:
        elapsed = time.time() - start_time
        result['time_seconds'] = round(elapsed, 2)
        result['error'] = f'exception: {str(e)}'
    
    return result


# ========== BATCH TESTING ==========

def test_all_prompts_on_page(pdf_file, page_num, prompts, output_base_dir, timeout=30, verbose=True):
    """
    Test all prompts on a single page.
    
    Args:
        pdf_file (str): Path to PDF file
        page_num (int): Page number
        prompts (list): List of prompt configurations
        output_base_dir (str): Base output directory
        timeout (int): Timeout per prompt
        verbose (bool): Print progress
        
    Returns:
        list: List of results (one per prompt)
    """
    
    results = []
    
    if verbose:
        print(f"\n  Page {page_num}/{count_pdf_pages(pdf_file)}")
    
    for idx, prompt in enumerate(prompts, 1):
        if verbose:
            print(f"    [{idx}/{len(prompts)}] Testing: {prompt['name']:30s}", end=" ", flush=True)
        
        result = test_single_page(pdf_file, page_num, prompt, output_base_dir, timeout)
        results.append(result)
        
        if verbose:
            if result['success']:
                print(f"✓ {result['time_seconds']:5.1f}s  (elements: {result['elements_count']}, tables: {result['tables_count']})")
            elif result['error'] == 'timeout':
                print(f"⏱️  TIMEOUT ({timeout}s)")
            else:
                print(f"✗ {result['error']}")
    
    return results


def test_all_pages_with_prompt(pdf_file, prompt, output_base_dir, timeout=30, verbose=True):
    """
    Test single prompt on all pages of a document.
    
    Args:
        pdf_file (str): Path to PDF file
        prompt (dict): Prompt configuration
        output_base_dir (str): Base output directory
        timeout (int): Timeout per page
        verbose (bool): Print progress
        
    Returns:
        list: List of results (one per page)
    """
    
    page_count = count_pdf_pages(pdf_file)
    results = []
    
    if verbose:
        print(f"\nPrompt: {prompt['name']}")
        print(f"File: {Path(pdf_file).name} ({page_count} pages)")
    
    for page_num in range(1, page_count + 1):
        if verbose:
            print(f"  Page {page_num}/{page_count}:", end=" ", flush=True)
        
        result = test_single_page(pdf_file, page_num, prompt, output_base_dir, timeout)
        results.append(result)
        
        if verbose:
            if result['success']:
                print(f"✓ {result['time_seconds']:5.1f}s")
            elif result['error'] == 'timeout':
                print(f"⏱️  TIMEOUT")
            else:
                print(f"✗ {result['error']}")
    
    return results


def run_full_test(pdf_files, prompts, output_base_dir, timeout=30, verbose=True):
    """
    Master function: Test all prompts on all pages of all files.
    
    Args:
        pdf_files (list): List of PDF file paths
        prompts (list): List of prompt configurations
        output_base_dir (str): Base output directory
        timeout (int): Timeout per test
        verbose (bool): Print progress
        
    Returns:
        dict: Complete test results
            {
                'total_tests': 190,
                'total_files': 2,
                'total_pages': 19,
                'total_prompts': 10,
                'results': [...],
                'summary': {...},
                'start_time': '...',
                'end_time': '...',
                'duration_seconds': 123.45
            }
    """
    
    start_time = datetime.now()
    all_results = []
    
    # Count totals
    total_pages = sum(count_pdf_pages(f) for f in pdf_files)
    total_tests = total_pages * len(prompts)
    
    if verbose:
        print("="*80)
        print("STARTING FULL TEST")
        print("="*80)
        print(f"\nFiles: {len(pdf_files)}")
        print(f"Total pages: {total_pages}")
        print(f"Prompts: {len(prompts)}")
        print(f"Total tests: {total_tests}")
        print(f"Timeout per test: {timeout}s")
        print(f"Estimated time: {(total_tests * 15) / 60:.1f} - {(total_tests * 30) / 60:.1f} minutes")
        print("\n" + "="*80)
    
    # Test each file
    for file_idx, pdf_file in enumerate(pdf_files, 1):
        page_count = count_pdf_pages(pdf_file)
        
        if verbose:
            print(f"\n[{file_idx}/{len(pdf_files)}] File: {Path(pdf_file).name} ({page_count} pages)")
            print("-"*80)
        
        # Test each page
        for page_num in range(1, page_count + 1):
            page_results = test_all_prompts_on_page(
                pdf_file, 
                page_num, 
                prompts, 
                output_base_dir, 
                timeout, 
                verbose
            )
            all_results.extend(page_results)
    
    # Calculate summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    successful = [r for r in all_results if r['success']]
    timeouts = [r for r in all_results if r['error'] == 'timeout']
    errors = [r for r in all_results if r['error'] and r['error'] != 'timeout']
    
    summary = {
        'total_tests': len(all_results),
        'successful': len(successful),
        'timeouts': len(timeouts),
        'errors': len(errors),
        'success_rate': len(successful) / len(all_results) * 100 if all_results else 0,
        'avg_time_success': sum(r['time_seconds'] for r in successful) / len(successful) if successful else 0,
        'total_elements': sum(r['elements_count'] for r in successful),
        'total_tables': sum(r['tables_count'] for r in successful),
    }
    
    result_package = {
        'total_tests': total_tests,
        'total_files': len(pdf_files),
        'total_pages': total_pages,
        'total_prompts': len(prompts),
        'results': all_results,
        'summary': summary,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_seconds': round(duration, 2)
    }
    
    if verbose:
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)
        print(f"\nTotal tests: {len(all_results)}")
        print(f"Successful: {len(successful)} ({summary['success_rate']:.1f}%)")
        print(f"Timeouts: {len(timeouts)}")
        print(f"Errors: {len(errors)}")
        print(f"\nTotal time: {duration:.1f}s ({duration/60:.1f} minutes)")
        print(f"Average time (successful): {summary['avg_time_success']:.1f}s")
        print(f"\nTotal elements found: {summary['total_elements']}")
        print(f"Total tables found: {summary['total_tables']}")
        print("="*80)
    
    return result_package


# ========== TESTING ==========

if __name__ == "__main__":
    # Test the engine
    print("="*80)
    print("TEST ENGINE - STANDALONE TEST")
    print("="*80)
    
    from prompts_config import get_all_prompts
    
    # Get prompts
    prompts = get_all_prompts()
    print(f"\nLoaded {len(prompts)} prompts")
    
    # Test single page (if you have a test file)
    # Uncomment and modify path to test:
    
    # test_file = "input/test.pdf"
    # if Path(test_file).exists():
    #     print(f"\nTesting single page with first prompt...")
    #     result = test_single_page(test_file, 1, prompts[0], "test_output", timeout=30)
    #     print(f"\nResult: {result}")
    # else:
    #     print(f"\nTest file not found: {test_file}")
    
    print("\n✓ Test engine ready!")
    print("\nUsage:")
    print("  from test_engine import run_full_test")
    print("  results = run_full_test(pdf_files, prompts, output_dir)")
    print()