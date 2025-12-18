"""
MultiPage Processor Module
Orchestrates multi-page document processing.
Handles PDFs and multi-image documents, combining results from multiple pages.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import time
from dataclasses import dataclass

from ..processors import PDFProcessor, ImageProcessor
from ..storage import OutputManager, DirectoryBuilder
from ..utils import is_pdf, is_supported_image, get_file_stem
from .base_extractor import BaseExtractor, ExtractionResult
from ..config import get_default_output_config

@dataclass
class PageResult:
    """Result for a single page"""
    page_number: int
    extraction_result: ExtractionResult
    page_image_path: str
    output_dir: str


@dataclass
class DocumentResult:
    """
    Complete result for multi-page document processing.
    """
    input_file: str
    output_dir: str
    page_count: int
    page_results: List[PageResult]
    total_processing_time: float
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def get_total_elements(self) -> int:
        """Get total elements across all pages"""
        return sum(pr.extraction_result.get_element_count() for pr in self.page_results)
    
    def get_successful_pages(self) -> int:
        """Get number of successfully processed pages"""
        return sum(1 for pr in self.page_results if pr.extraction_result.success)
    
    def get_failed_pages(self) -> List[int]:
        """Get list of failed page numbers"""
        return [pr.page_number for pr in self.page_results if not pr.extraction_result.success]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'input_file': self.input_file,
            'output_dir': self.output_dir,
            'page_count': self.page_count,
            'successful_pages': self.get_successful_pages(),
            'failed_pages': self.get_failed_pages(),
            'total_elements': self.get_total_elements(),
            'total_processing_time': self.total_processing_time,
            'error_message': self.error_message,
            'pages': [
                {
                    'page_number': pr.page_number,
                    'success': pr.extraction_result.success,
                    'elements': pr.extraction_result.get_element_count(),
                    'processing_time': pr.extraction_result.processing_time
                }
                for pr in self.page_results
            ],
            'metadata': self.metadata
        }


class MultiPageProcessor:
    """
    Orchestrates multi-page document processing.
    
    Handles:
    - PDF to image conversion
    - Page-by-page OCR extraction
    - Result organization and storage
    - Page combination
    - Metadata generation
    """
    
    def __init__(
        self,
        extractor: BaseExtractor,
        output_config: Optional[Any] = None
    ):
        """
        Initialize multi-page processor.
        
        Args:
            extractor: Extractor instance (OllamaExtractor, etc.)
            output_config: Output configuration (None = use defaults)
            
        Example:
            >>> from extractors import OllamaExtractor, MultiPageProcessor
            >>> extractor = OllamaExtractor()
            >>> processor = MultiPageProcessor(extractor)
            >>> result = processor.process_document("manual.pdf")
        """
        self.extractor = extractor
        
        # Get output config
        if output_config is None:
            # from config import get_default_output_config
            output_config = get_default_output_config()
        self.output_config = output_config
        
        # Initialize processors
        self.pdf_processor = PDFProcessor(dpi=300)
        self.image_processor = ImageProcessor()
        
        # Initialize output manager and directory builder
        self.output_manager = OutputManager(output_config)
        self.dir_builder = DirectoryBuilder(output_config)
    
    def process_document(
        self,
        file_path: str,
        custom_prompt: Optional[str] = None,
        page_range: Optional[tuple] = None
    ) -> DocumentResult:
        """
        Process a document (PDF or image).
        
        Args:
            file_path: Path to document file
            custom_prompt: Override default prompt
            page_range: Optional (start, end) page numbers for PDFs
            
        Returns:
            DocumentResult: Complete processing result
            
        Example:
            >>> processor = MultiPageProcessor(extractor)
            >>> result = processor.process_document("manual.pdf")
            >>> print(f"Processed {result.page_count} pages")
            >>> print(f"Output: {result.output_dir}")
        """
        file_path = Path(file_path)
        
        # Validate file exists
        if not file_path.exists():
            return self._create_error_result(
                file_path=str(file_path),
                error_message=f"File not found: {file_path}"
            )
        
        start_time = time.time()
        
        try:
            # Create output directory structure
            output_dir = self.dir_builder.create_document_structure(str(file_path))
            
            # Get list of images to process
            if is_pdf(str(file_path)):
                images = self._process_pdf(str(file_path), output_dir, page_range)
            elif is_supported_image(str(file_path)):
                images = [str(file_path)]
            else:
                return self._create_error_result(
                    file_path=str(file_path),
                    error_message=f"Unsupported file format: {file_path.suffix}"
                )
            
            # Process each page
            page_results = []
            for page_num, image_path in enumerate(images, 1):
                print(f"Processing page {page_num}/{len(images)}...")
                
                page_result = self._process_page(
                    image_path=image_path,
                    page_number=page_num,
                    output_dir=output_dir,
                    custom_prompt=custom_prompt
                )
                
                page_results.append(page_result)
            
            # Create combined output
            if self.output_config.create_combined and len(page_results) > 1:
                self._create_combined_output(page_results, output_dir)
            
            # Generate metadata
            total_time = time.time() - start_time
            metadata = self._generate_metadata(
                file_path=str(file_path),
                page_results=page_results,
                total_time=total_time
            )
            
            # Save metadata
            if self.output_config.save_metadata:
                self._save_metadata(metadata, output_dir)
            
            # Create result
            return DocumentResult(
                input_file=str(file_path),
                output_dir=output_dir,
                page_count=len(page_results),
                page_results=page_results,
                total_processing_time=total_time,
                success=True,
                metadata=metadata
            )
        
        except Exception as e:
            return self._create_error_result(
                file_path=str(file_path),
                error_message=f"Processing failed: {str(e)}"
            )
    
    def _process_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        page_range: Optional[tuple]
    ) -> List[str]:
        """
        Convert PDF to images.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Base output directory
            page_range: Optional page range
            
        Returns:
            List[str]: List of image paths
        """
        # Create temp directory for page images
        pages_temp_dir = Path(output_dir) / "temp_pages"
        pages_temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert PDF to images
        images = self.pdf_processor.pdf_to_images(
            pdf_path=pdf_path,
            output_dir=str(pages_temp_dir),
            page_range=page_range
        )
        
        return images
    
    def _process_page(
        self,
        image_path: str,
        page_number: int,
        output_dir: str,
        custom_prompt: Optional[str]
    ) -> PageResult:
        """
        Process a single page.
        
        Args:
            image_path: Path to page image
            page_number: Page number
            output_dir: Base output directory
            custom_prompt: Optional custom prompt
            
        Returns:
            PageResult: Page processing result
        """
        # Create page output directory
        page_dir = self.dir_builder.create_page_directory(output_dir, page_number)
        
        # ========== NEW: Resize image to 1024x1024 for OCR ==========
        from PIL import Image
        print(f"  [PRE-PROCESSING] Resizing image for OCR...")
        
        # Load original image
        original_img = Image.open(image_path)
        original_width, original_height = original_img.size
        print(f"    Original size: {original_width} × {original_height}")
        
        # Resize to 1024x1024 (DeepSeek OCR Base resolution)
        target_size = 1024
        resized_img = original_img.resize((target_size, target_size), Image.LANCZOS)
        
        # Save resized image for OCR processing
        resized_path = Path(image_path).parent / f"{Path(image_path).stem}_ocr.png"
        resized_img.save(resized_path)
        print(f"    Resized to: {target_size} × {target_size}")
        
        # Store scale factors for later (if needed)
        scale_x = original_width / target_size
        scale_y = original_height / target_size
        # ===========================================================

        # Extract with retry if configured
        if hasattr(self.extractor, 'config') and self.extractor.config.retry_on_failure:
            extraction_result = self.extractor.extract_with_retry(
                # image_path=image_path,
                image_path=str(resized_path),
                custom_prompt=custom_prompt
            )
        else:
            extraction_result = self.extractor.extract(
                # image_path=image_path,
                image_path=str(resized_path),
                custom_prompt=custom_prompt
            )
        

        # ========== NEW: Scale bboxes back to original size ==========
        # (Optional - only if I want to draw on original size) then i can use the scale_x , scale_y
        # For now, we'll save everything at 1024x1024 size
        # ==============================================================

        # Save page results
        self.output_manager.save_page_result(
            result=extraction_result,
            page_number=page_number,
            page_dir=page_dir
        )
        
        # Save annotated image if configured
        if self.output_config.save_per_page.get('annotated_image', False):
            self._create_page_annotation(
                # image_path=image_path,
                image_path=str(resized_path),
                extraction_result=extraction_result,
                page_dir=page_dir,
                page_number=page_number
            )
            
        
        return PageResult(
            page_number=page_number,
            extraction_result=extraction_result,
            # page_image_path=image_path,
            page_image_path=str(resized_path),
            output_dir=page_dir
        )
    
    def _create_page_annotation(
        self,
        image_path: str,
        extraction_result: ExtractionResult,
        page_dir: str,
        page_number: int
    ):
        """
        Create annotated image with bounding boxes.
        
        Args:
            image_path: Path to original image
            extraction_result: Extraction result with elements
            page_dir: Page output directory
            page_number: Page number
        """
        try:
            from ..visualizers import BBoxVisualizer
            from PIL import Image
            import shutil

            # Get visualization config from output_config or use defaults
            show_labels = getattr(self.output_config, 'show_labels', True)
            box_width = getattr(self.output_config, 'box_width', 3)
            color_scheme = getattr(self.output_config, 'color_scheme', 'default')
            
            # Create visualizer
            visualizer = BBoxVisualizer(
                show_labels=show_labels,
                show_ids=True,
                box_width=box_width,
                color_scheme=color_scheme
            )

            # ========== FIX: Copy the RESIZED image as original ==========
            original_path = Path(page_dir) / f"page_{page_number:03d}_original.png"
        
            # Copy the resized image (1024×1024) to output directory
            if not original_path.exists():
                shutil.copy2(image_path, original_path)  # ← image_path is already resized!
                print(f"  ✓ Saved original image: {original_path.name}")
            # ====================================================
            # Create annotated image path
            annotated_path = Path(page_dir) / f"page_{page_number:03d}_annotated.png"
            
            # Only visualize if we have elements with bounding boxes
            elements = extraction_result.get_elements()
            if elements:
                visualizer.visualize(
                    image_path=image_path,
                    elements=elements,
                    output_path=str(annotated_path)
                )
                print(f"  ✓ Created annotation: {annotated_path.name}")
                # ========== ADD THIS SECTION ==========
                # Create side-by-side comparison if configured
                create_comparison = getattr(self.output_config, 'create_comparison', True)
                if create_comparison:
                    comparison_path = Path(page_dir) / f"page_{page_number:03d}_comparison.png"
                    visualizer.create_comparison(
                        original_path=image_path,
                        annotated_path=str(annotated_path),
                        output_path=str(comparison_path)
                    )
                    print(f"  ✓ Created comparison: {comparison_path.name}")
                # ======================================
            else:
                print(f"  ⚠ No elements to visualize for page {page_number}")
        
        except Exception as e:
            # Don't fail the entire process if visualization fails
            print(f"  ⚠ Warning: Could not create annotation for page {page_number}: {e}")



    def _create_combined_output(
        self,
        page_results: List[PageResult],
        output_dir: str
    ):
        """
        Create combined output from all pages.
        
        Args:
            page_results: List of page results
            output_dir: Base output directory
        """
        combined_dir = Path(output_dir) / self.output_config.combined_subfolder
        combined_dir.mkdir(parents=True, exist_ok=True)
        
        # Combine markdown
        if "markdown" in self.output_config.combined_formats:
            self._create_combined_markdown(page_results, combined_dir)
        
        # Combine JSON
        if "json" in self.output_config.combined_formats:
            self._create_combined_json(page_results, combined_dir)
    
    def _create_combined_markdown(
        self,
        page_results: List[PageResult],
        combined_dir: Path
    ):
        """Create combined markdown file"""
        markdown_content = []
        
        for page_result in page_results:
            markdown_content.append(f"# Page {page_result.page_number}\n")
            
            # Extract text from elements
            for element in page_result.extraction_result.get_elements():
                markdown_content.append(element.content)
                markdown_content.append("\n")
            
            markdown_content.append("\n---\n\n")
        
        # Save combined markdown
        output_file = combined_dir / "full_document.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))
    
    def _create_combined_json(
        self,
        page_results: List[PageResult],
        combined_dir: Path
    ):
        """Create combined JSON file"""
        combined_data = {
            'pages': [
                {
                    'page_number': pr.page_number,
                    'elements': pr.extraction_result.parse_result.to_dict()
                }
                for pr in page_results
            ]
        }
        
        output_file = combined_dir / "full_document.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    def _generate_metadata(
        self,
        file_path: str,
        page_results: List[PageResult],
        total_time: float
    ) -> Dict[str, Any]:
        """Generate metadata for document"""
        return {
            'input_file': file_path,
            'page_count': len(page_results),
            'total_processing_time': total_time,
            'successful_pages': sum(1 for pr in page_results if pr.extraction_result.success),
            'total_elements': sum(pr.extraction_result.get_element_count() for pr in page_results),
            'model_used': self.extractor.get_extractor_name(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _save_metadata(self, metadata: dict, output_dir: str):
        """Save metadata to file"""
        metadata_file = Path(output_dir) / self.output_config.metadata_filename
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _create_error_result(
        self,
        file_path: str,
        error_message: str
    ) -> DocumentResult:
        """Create error result"""
        return DocumentResult(
            input_file=file_path,
            output_dir="",
            page_count=0,
            page_results=[],
            total_processing_time=0.0,
            success=False,
            error_message=error_message
        )


if __name__ == "__main__":
    print("Testing multipage_processor.py...\n")
    
    print("Note: Full testing requires:")
    print("  - Ollama running")
    print("  - Storage module implemented")
    print("  - Test PDF/image file")
    
    print("\n✅ multipage_processor.py structure verified!")
    print("\nUsage example:")
    print("""
    from extractors import OllamaExtractor, MultiPageProcessor
    from config import OCRConfig
    
    # Setup
    config = OCRConfig(model_name="deepseek-ocr:3b")
    extractor = OllamaExtractor(config)
    processor = MultiPageProcessor(extractor)
    
    # Process document
    result = processor.process_document("manual.pdf")
    
    print(f"Processed {result.page_count} pages")
    print(f"Output: {result.output_dir}")
    print(f"Total elements: {result.get_total_elements()}")
    """)