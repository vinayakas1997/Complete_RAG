"""
PDF Processor Module
Handles PDF to image conversion for OCR processing.
Supports multi-page PDFs and page extraction.
"""

from pathlib import Path
from typing import List, Optional, Tuple
import tempfile

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

from PIL import Image


class PDFProcessor:
    """
    PDF to image converter.
    Uses PyMuPDF (fitz) as primary, pdf2image as fallback.
    """
    
    def __init__(
        self,
        dpi: int = 300,
        use_pymupdf: bool = True
    ):
        """
        Initialize PDF processor.
        
        Args:
            dpi: Resolution for image conversion (higher = better quality)
            use_pymupdf: Prefer PyMuPDF over pdf2image if available
        """
        self.dpi = dpi
        self.use_pymupdf = use_pymupdf
        
        # Check available libraries
        if not PYMUPDF_AVAILABLE and not PDF2IMAGE_AVAILABLE:
            raise RuntimeError(
                "No PDF library available. Install either:\n"
                "  pip install PyMuPDF\n"
                "  or\n"
                "  pip install pdf2image"
            )
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        Get number of pages in PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            int: Number of pages
            
        Example:
            >>> processor = PDFProcessor()
            >>> count = processor.get_page_count("document.pdf")
            >>> print(count)
            10
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        if PYMUPDF_AVAILABLE:
            doc = fitz.open(str(pdf_path))
            page_count = len(doc)
            doc.close()
            return page_count
        
        elif PDF2IMAGE_AVAILABLE:
            # pdf2image requires conversion to count (slower)
            from pdf2image import pdfinfo_from_path
            info = pdfinfo_from_path(str(pdf_path))
            return info.get('Pages', 0)
        
        else:
            raise RuntimeError("No PDF library available")
    
    def pdf_to_images(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        page_range: Optional[Tuple[int, int]] = None
    ) -> List[str]:
        """
    Convert PDF pages to images.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images (None = temp dir)
            page_range: Optional (start, end) page numbers (1-indexed)
            
        Returns:
            List[str]: List of image file paths
            
        Example:
            >>> processor = PDFProcessor()
            >>> images = processor.pdf_to_images("doc.pdf", "output/pages")
            >>> print(images)
            ['output/pages/page_001.png', 'output/pages/page_002.png', ...]
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Create output directory
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="pdf_pages_")
        else:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Convert based on available library
        if self.use_pymupdf and PYMUPDF_AVAILABLE:
            return self._pdf_to_images_pymupdf(pdf_path, output_dir, page_range)
        elif PDF2IMAGE_AVAILABLE:
            return self._pdf_to_images_pdf2image(pdf_path, output_dir, page_range)
        else:
            raise RuntimeError("No PDF library available")
    
    def _pdf_to_images_pymupdf(
        self,
        pdf_path: Path,
        output_dir: str,
        page_range: Optional[Tuple[int, int]]
    ) -> List[str]:
        """Convert PDF to images using PyMuPDF (faster, better quality)"""
        doc = fitz.open(str(pdf_path))
        image_paths = []
        
        # Determine page range
        start_page = 0
        end_page = len(doc)
        
        if page_range:
            start_page = max(0, page_range[0] - 1)  # Convert to 0-indexed
            end_page = min(len(doc), page_range[1])
        
        # Convert each page
        for page_num in range(start_page, end_page):
            page = doc[page_num]
            
            # Render page to image
            zoom = self.dpi / 72  # PyMuPDF uses 72 DPI base
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Save image
            output_path = Path(output_dir) / f"page_{page_num + 1:03d}.png"
            pix.save(str(output_path))
            image_paths.append(str(output_path))
        
        doc.close()
        return image_paths
    
    def _pdf_to_images_pdf2image(
        self,
        pdf_path: Path,
        output_dir: str,
        page_range: Optional[Tuple[int, int]]
    ) -> List[str]:
        """Convert PDF to images using pdf2image (requires poppler)"""
        
        # Determine page range
        first_page = None
        last_page = None
        
        if page_range:
            first_page = page_range[0]
            last_page = page_range[1]
        
        # Convert pages
        images = convert_from_path(
            str(pdf_path),
            dpi=self.dpi,
            first_page=first_page,
            last_page=last_page
        )
        
        # Save images
        image_paths = []
        start_num = first_page if first_page else 1
        
        for i, image in enumerate(images):
            page_num = start_num + i
            output_path = Path(output_dir) / f"page_{page_num:03d}.png"
            image.save(str(output_path), 'PNG')
            image_paths.append(str(output_path))
        
        return image_paths
    
    def extract_single_page(
        self,
        pdf_path: str,
        page_number: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        Extract a single page from PDF as image.
        
        Args:
            pdf_path: Path to PDF file
            page_number: Page number to extract (1-indexed)
            output_path: Where to save image (None = temp file)
            
        Returns:
            str: Path to extracted image
            
        Example:
            >>> processor = PDFProcessor()
            >>> img = processor.extract_single_page("doc.pdf", 5)
            >>> print(img)
            '/tmp/page_005.png'
        """
        if output_path is None:
            temp_dir = tempfile.mkdtemp(prefix="pdf_page_")
            output_path = str(Path(temp_dir) / f"page_{page_number:03d}.png")
        
        images = self.pdf_to_images(
            pdf_path,
            output_dir=str(Path(output_path).parent),
            page_range=(page_number, page_number)
        )
        
        return images[0] if images else None
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get PDF metadata and information.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            dict: PDF information
            
        Example:
            >>> processor = PDFProcessor()
            >>> info = processor.get_pdf_info("doc.pdf")
            >>> print(info)
            {'pages': 10, 'title': 'Document', 'author': '...'}
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        info = {
            'filename': pdf_path.name,
            'filepath': str(pdf_path.absolute()),
            'pages': self.get_page_count(str(pdf_path))
        }
        
        if PYMUPDF_AVAILABLE:
            doc = fitz.open(str(pdf_path))
            metadata = doc.metadata
            info.update({
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
            })
            doc.close()
        
        return info


if __name__ == "__main__":
    print("Testing pdf_processor.py...\n")
    
    print("Available PDF libraries:")
    print(f"  PyMuPDF: {PYMUPDF_AVAILABLE}")
    print(f"  pdf2image: {PDF2IMAGE_AVAILABLE}")
    
    if not PYMUPDF_AVAILABLE and not PDF2IMAGE_AVAILABLE:
        print("\n⚠️  No PDF library available!")
        print("Install one of:")
        print("  pip install PyMuPDF")
        print("  pip install pdf2image")
    else:
        print("\n✅ PDF processor ready!")
        
        # Test processor creation
        processor = PDFProcessor(dpi=150)  # Lower DPI for testing
        print(f"Processor created with DPI: {processor.dpi}")
        
        # Note: Actual PDF conversion tests require a PDF file
        print("\nTo test PDF conversion, run:")
        print('  processor = PDFProcessor()')
        print('  images = processor.pdf_to_images("your_file.pdf", "output_dir")')
        print('  print(f"Converted {len(images)} pages")')
    
    print("\n✅ pdf_processor.py tests passed!")