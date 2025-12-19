"""
Output Manager Module
Manages saving extraction results to various output formats.
Handles raw output, JSON, markdown, and metadata files.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json

from ..config import OutputConfig
from ..extractors.base_extractor import ExtractionResult


class OutputManager:
    """
    Manages output file creation and saving.
    
    Handles saving:
    - Raw OCR output text
    - Grounding JSON (parsed elements)
    - Markdown conversion
    - Metadata files
    """
    
    def __init__(self, output_config: OutputConfig):
        """
        Initialize output manager.
        
        Args:
            output_config: Output configuration
            
        Example:
            >>> from config import get_default_output_config
            >>> config = get_default_output_config()
            >>> manager = OutputManager(config)
        """
        self.config = output_config
    
    def save_page_result(
        self,
        result: ExtractionResult,
        page_number: int,
        page_dir: str
    ):
        """
        Save all outputs for a single page.
        
        Args:
            result: Extraction result
            page_number: Page number
            page_dir: Directory to save outputs
            
        Example:
            >>> manager.save_page_result(extraction_result, 1, "output/doc/pages/page_001")
        """
        page_dir = Path(page_dir)
        page_name = self.config.page_naming_format.format(num=page_number)
        
        # Save raw output
        if self.config.save_per_page.get('raw_output', True):
            self._save_raw_output(result, page_dir)
        
        # Save grounding JSON
        if self.config.save_per_page.get('grounding_json', True):
            self._save_grounding_json(result, page_dir)
        
        # Save markdown
        if self.config.save_per_page.get('markdown', False):
            self._save_markdown(result, page_dir, page_name)
    
    def _save_raw_output(self, result: ExtractionResult, page_dir: Path):
        """
        Save raw OCR output text.
        
        Args:
            result: Extraction result
            page_dir: Output directory
        """
        output_file = page_dir / "raw_output.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.raw_output)
        
        print(f"  ✓ Saved raw output: {output_file.name}")
    
    def _save_grounding_json(self, result: ExtractionResult, page_dir: Path):
        """
        Save parsed elements as JSON.
        
        Args:
            result: Extraction result
            page_dir: Output directory
        """
        output_file = page_dir / "grounding.json"
        
        # Convert to dictionary
        data = result.parse_result.to_dict()
        
        # Add extraction metadata
        data['extraction_metadata'] = {
            'model': result.model_name,
            'processing_time': result.processing_time,
            'prompt_used': result.prompt_used[:100] + "..." if len(result.prompt_used) > 100 else result.prompt_used
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Saved grounding JSON: {output_file.name}")
    
    def _save_markdown(self, result: ExtractionResult, page_dir: Path, page_name: str):
        """
        Save content as markdown.
        
        Args:
            result: Extraction result
            page_dir: Output directory
            page_name: Base name for file
        """
        output_file = page_dir / f"{page_name}.md"
        
        # Convert elements to markdown
        markdown_content = self._elements_to_markdown(result)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"  ✓ Saved markdown: {output_file.name}")
    
    def _elements_to_markdown(self, result: ExtractionResult) -> str:
        """
        Convert parsed elements to markdown format.
        
        Args:
            result: Extraction result
            
        Returns:
            str: Markdown content
        """
        markdown_lines = []
        
        for element in result.get_elements():
            element_type = element.element_type
            content = element.content
            
            # Format based on element type
            if element_type.startswith('heading_'):
                level = element_type.split('_')[1]
                markdown_lines.append(f"{'#' * int(level)} {content}\n")
            
            elif element_type in ['title', 'sub_title']:
                markdown_lines.append(f"## {content}\n")
            
            elif element_type == 'table':
                # Table is already in markdown/HTML format
                markdown_lines.append(f"{content}\n")
            
            elif element_type == 'list':
                markdown_lines.append(f"{content}\n")
            
            elif element_type == 'code_block':
                markdown_lines.append(f"```\n{content}\n```\n")
            
            elif element_type in ['image', 'figure']:
                markdown_lines.append(f"![{element_type}](bbox: {element.bbox})\n")
                if element.metadata and 'description' in element.metadata:
                    markdown_lines.append(f"*{element.metadata['description']}*\n")
            
            else:
                # Default: just add content as paragraph
                markdown_lines.append(f"{content}\n")
            
            markdown_lines.append("\n")
        
        return ''.join(markdown_lines)
    
    def save_combined_output(
        self,
        combined_data: Dict[str, Any],
        output_dir: str,
        format: str = "markdown"
    ):
        """
        Save combined output from all pages.
        
        Args:
            combined_data: Combined data from all pages
            output_dir: Output directory
            format: Output format (markdown or json)
            
        Example:
            >>> manager.save_combined_output(data, "output/doc/combined", "markdown")
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "markdown":
            output_file = output_dir / "full_document.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(combined_data.get('content', ''))
            print(f"✓ Saved combined markdown: {output_file}")
        
        elif format == "json":
            output_file = output_dir / "full_document.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved combined JSON: {output_file}")
    
    def save_metadata(
        self,
        metadata: Dict[str, Any],
        output_dir: str
    ):
        """
        Save document metadata.
        
        Args:
            metadata: Metadata dictionary
            output_dir: Output directory
            
        Example:
            >>> manager.save_metadata(metadata, "output/doc")
        """
        output_dir = Path(output_dir)
        output_file = output_dir / self.config.metadata_filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved metadata: {output_file}")
    
    def save_statistics(
        self,
        statistics: Dict[str, Any],
        output_dir: str,
        filename: str = "statistics.json"
    ):
        """
        Save processing statistics.
        
        Args:
            statistics: Statistics dictionary
            output_dir: Output directory
            filename: Output filename
            
        Example:
            >>> stats = {
            ...     'total_pages': 10,
            ...     'total_elements': 245,
            ...     'processing_time': 45.2
            ... }
            >>> manager.save_statistics(stats, "output/doc")
        """
        output_dir = Path(output_dir)
        output_file = output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved statistics: {output_file}")
    
    def create_summary_report(
        self,
        results: list,
        output_dir: str
    ) -> str:
        """
        Create human-readable summary report.
        
        Args:
            results: List of page results
            output_dir: Output directory
            
        Returns:
            str: Path to summary report
            
        Example:
            >>> report_path = manager.create_summary_report(page_results, "output/doc")
        """
        output_dir = Path(output_dir)
        output_file = output_dir / "summary_report.txt"
        
        lines = []
        lines.append("="*60)
        lines.append("OCR PROCESSING SUMMARY REPORT")
        lines.append("="*60)
        lines.append("")
        
        # Overall stats
        total_pages = len(results)
        total_elements = sum(r.extraction_result.get_element_count() for r in results)
        successful = sum(1 for r in results if r.extraction_result.success)
        
        lines.append(f"Total Pages: {total_pages}")
        lines.append(f"Successful Pages: {successful}")
        lines.append(f"Failed Pages: {total_pages - successful}")
        lines.append(f"Total Elements Extracted: {total_elements}")
        lines.append("")
        
        # Per-page breakdown
        lines.append("Per-Page Breakdown:")
        lines.append("-"*60)
        for result in results:
            page_num = result.page_number
            success = "✓" if result.extraction_result.success else "✗"
            elements = result.extraction_result.get_element_count()
            time = result.extraction_result.processing_time
            
            lines.append(f"Page {page_num:3d} {success} - {elements:3d} elements - {time:.2f}s")
        
        lines.append("")
        lines.append("="*60)
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✓ Saved summary report: {output_file}")
        return str(output_file)


if __name__ == "__main__":
    print("Testing output_manager.py...\n")
    
    # Test 1: Create manager
    print("Test 1: Create Output Manager")
    print("-" * 60)
    from config import get_default_output_config
    
    config = get_default_output_config()
    manager = OutputManager(config)
    print(f"Save raw output: {config.save_per_page.get('raw_output')}")
    print(f"Save grounding JSON: {config.save_per_page.get('grounding_json')}")
    
    # Test 2: Test with mock result
    print("\n" + "="*60)
    print("Test 2: Save Mock Result")
    print("-" * 60)
    
    import tempfile
    from ..parsers import ParsedElement, ParseResult
    from ..extractors import ExtractionResult
    
    # Create mock result
    elements = [
        ParsedElement(1, "title", [10, 20, 100, 40], "Test Document"),
        ParsedElement(2, "text", [10, 50, 400, 100], "This is test content."),
        ParsedElement(3, "table", [10, 110, 400, 200], "<table><tr><td>Data</td></tr></table>"),
    ]
    
    parse_result = ParseResult(
        elements=elements,
        raw_text="Raw output...",
        parser_type="test_parser",
        success=True
    )
    
    extraction_result = ExtractionResult(
        raw_output="<|ref|>title<|/ref|><|det|>[[10,20,100,40]]<|/det|>Test Document",
        parse_result=parse_result,
        model_name="test-model",
        prompt_used="Test prompt",
        image_path="test.png",
        processing_time=1.5,
        success=True
    )
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    page_dir = temp_dir / "page_001"
    page_dir.mkdir(parents=True, exist_ok=True)
    
    # Save result
    manager.save_page_result(extraction_result, 1, str(page_dir))
    
    # Check files created
    print("\nFiles created:")
    for file in page_dir.iterdir():
        print(f"  - {file.name}")
    
    # Test 3: Save metadata
    print("\n" + "="*60)
    print("Test 3: Save Metadata")
    print("-" * 60)
    
    metadata = {
        'document': 'test.pdf',
        'pages': 3,
        'processing_time': 10.5
    }
    
    manager.save_metadata(metadata, str(temp_dir))
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    
    print("\n✅ output_manager.py tests passed!")