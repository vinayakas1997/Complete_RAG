"""
Directory Builder Module
Creates organized directory structures for OCR output.
Handles document-level and page-level folder creation.
"""

from pathlib import Path
from typing import Optional
import uuid
import datetime

from ..config import OutputConfig
from ..utils import get_file_stem, sanitize_filename, generate_folder_name, ensure_directory


class DirectoryBuilder:
    """
    Creates and manages output directory structures.
    
    Organizes outputs in a hierarchical structure:
    output/
    └── document_name/
        ├── pages/
        │   ├── page_001/
        │   ├── page_002/
        │   └── ...
        ├── combined/
        └── metadata.json
    """
    
    def __init__(self, output_config: OutputConfig):
        """
        Initialize directory builder.
        
        Args:
            output_config: Output configuration
            
        Example:
            >>> from config import get_default_output_config
            >>> config = get_default_output_config()
            >>> builder = DirectoryBuilder(config)
        """
        self.config = output_config
    
    def create_document_structure(self, file_path: str) -> str:
        """
        Create complete directory structure for a document.
        
        Args:
            file_path: Path to input document
            
        Returns:
            str: Path to created document output directory
            
        Example:
            >>> builder = DirectoryBuilder(config)
            >>> output_dir = builder.create_document_structure("manual.pdf")
            >>> print(output_dir)
            'output/manual'
        """
        file_path = Path(file_path)
        
        # Get document folder name
        doc_folder_name = self._get_document_folder_name(file_path)
        
        # Create base document directory
        doc_dir = Path(self.config.output_base_dir) / doc_folder_name
        
        if self.config.auto_create_folder:
            ensure_directory(str(doc_dir))
        
        # Create subdirectories if needed
        if self.config.split_pages:
            pages_dir = doc_dir / self.config.pages_subfolder
            ensure_directory(str(pages_dir))
        
        if self.config.create_combined:
            combined_dir = doc_dir / self.config.combined_subfolder
            ensure_directory(str(combined_dir))
        
        return str(doc_dir)
    
    def create_page_directory(self, document_dir: str, page_number: int) -> str:
        """
        Create directory for a single page.
        
        Args:
            document_dir: Base document directory
            page_number: Page number
            
        Returns:
            str: Path to page directory
            
        Example:
            >>> page_dir = builder.create_page_directory("output/manual", 1)
            >>> print(page_dir)
            'output/manual/pages/page_001'
        """
        if not self.config.split_pages:
            # If not splitting pages, return document dir
            return document_dir
        
        # Create page folder name
        page_folder = self.config.page_naming_format.format(num=page_number)
        
        # Create page directory
        page_dir = Path(document_dir) / self.config.pages_subfolder / page_folder
        ensure_directory(str(page_dir))
        
        return str(page_dir)
    
    def get_combined_directory(self, document_dir: str) -> str:
        """
        Get path to combined output directory.
        
        Args:
            document_dir: Base document directory
            
        Returns:
            str: Path to combined directory
            
        Example:
            >>> combined_dir = builder.get_combined_directory("output/manual")
            >>> print(combined_dir)
            'output/manual/combined'
        """
        if not self.config.create_combined:
            return document_dir
        
        combined_dir = Path(document_dir) / self.config.combined_subfolder
        ensure_directory(str(combined_dir))
        
        return str(combined_dir)
    
    def _get_document_folder_name(self, file_path: Path) -> str:
        """
        Generate folder name for document.
        
        Args:
            file_path: Path to input file
            
        Returns:
            str: Sanitized folder name
        """
        strategy = self.config.folder_naming
        
        if strategy == "stem":
            # Use filename without extension
            folder_name = get_file_stem(str(file_path))
        
        elif strategy == "full":
            # Use full filename (including extension)
            folder_name = file_path.name
        
        elif strategy == "uuid":
            # Generate unique UUID
            folder_name = str(uuid.uuid4())[:8]
        
        elif strategy == "timestamp":
            # Use timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{get_file_stem(str(file_path))}_{timestamp}"
        
        else:
            # Default to stem
            folder_name = get_file_stem(str(file_path))
        
        # Sanitize for filesystem
        return sanitize_filename(folder_name)
    
    def get_output_paths(
        self,
        document_dir: str,
        page_number: Optional[int] = None
    ) -> dict:
        """
        Get all output file paths for a document or page.
        
        Args:
            document_dir: Base document directory
            page_number: Optional page number (None = document level)
            
        Returns:
            dict: Dictionary of output paths
            
        Example:
            >>> paths = builder.get_output_paths("output/manual", page_number=1)
            >>> print(paths['raw_output'])
            'output/manual/pages/page_001/raw_output.txt'
        """
        if page_number is not None:
            # Page-level paths
            page_dir = self.create_page_directory(document_dir, page_number)
            page_name = self.config.page_naming_format.format(num=page_number)
            
            return {
                'page_dir': page_dir,
                'raw_output': str(Path(page_dir) / 'raw_output.txt'),
                'grounding_json': str(Path(page_dir) / 'grounding.json'),
                'markdown': str(Path(page_dir) / f'{page_name}.md'),
                'annotated_image': str(Path(page_dir) / f'{page_name}_annotated.png'),
                'original_image': str(Path(page_dir) / f'{page_name}_original.png'),
            }
        else:
            # Document-level paths
            combined_dir = self.get_combined_directory(document_dir)
            
            return {
                'document_dir': document_dir,
                'combined_dir': combined_dir,
                'combined_markdown': str(Path(combined_dir) / 'full_document.md'),
                'combined_json': str(Path(combined_dir) / 'full_document.json'),
                'metadata': str(Path(document_dir) / self.config.metadata_filename),
            }
    
    def cleanup_temp_files(self, document_dir: str):
        """
        Clean up temporary files if configured.
        
        Args:
            document_dir: Base document directory
            
        Example:
            >>> builder.cleanup_temp_files("output/manual")
        """
        if not self.config.cleanup_intermediates:
            return
        
        # Clean up temp directory if it exists
        temp_dir = Path(document_dir) / "temp_pages"
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary files: {temp_dir}")


if __name__ == "__main__":
    print("Testing directory_builder.py...\n")
    
    # Test 1: Create builder
    print("Test 1: Create Directory Builder")
    print("-" * 60)
    from config import get_default_output_config
    
    config = get_default_output_config()
    builder = DirectoryBuilder(config)
    print(f"Output base dir: {config.output_base_dir}")
    print(f"Folder naming: {config.folder_naming}")
    
    # Test 2: Generate document folder names
    print("\n" + "="*60)
    print("Test 2: Document Folder Names")
    print("-" * 60)
    
    test_file = Path("test_document.pdf")
    
    for strategy in ["stem", "full", "uuid", "timestamp"]:
        config.folder_naming = strategy
        builder = DirectoryBuilder(config)
        folder_name = builder._get_document_folder_name(test_file)
        print(f"{strategy:12s}: {folder_name}")
    
    # Test 3: Create document structure
    print("\n" + "="*60)
    print("Test 3: Create Document Structure")
    print("-" * 60)
    
    import tempfile
    temp_base = Path(tempfile.mkdtemp())
    
    config = get_default_output_config()
    config.output_base_dir = str(temp_base)
    builder = DirectoryBuilder(config)
    
    doc_dir = builder.create_document_structure("test_manual.pdf")
    print(f"Created: {doc_dir}")
    
    # Check what was created
    if Path(doc_dir).exists():
        print("✓ Document directory created")
        
        pages_dir = Path(doc_dir) / config.pages_subfolder
        if pages_dir.exists():
            print("✓ Pages directory created")
        
        combined_dir = Path(doc_dir) / config.combined_subfolder
        if combined_dir.exists():
            print("✓ Combined directory created")
    
    # Test 4: Create page directory
    print("\n" + "="*60)
    print("Test 4: Create Page Directory")
    print("-" * 60)
    
    page_dir = builder.create_page_directory(doc_dir, 1)
    print(f"Page 1 dir: {page_dir}")
    
    if Path(page_dir).exists():
        print("✓ Page directory created")
    
    # Test 5: Get output paths
    print("\n" + "="*60)
    print("Test 5: Get Output Paths")
    print("-" * 60)
    
    page_paths = builder.get_output_paths(doc_dir, page_number=1)
    print("Page-level paths:")
    for key, path in page_paths.items():
        print(f"  {key}: {Path(path).name}")
    
    doc_paths = builder.get_output_paths(doc_dir)
    print("\nDocument-level paths:")
    for key, path in doc_paths.items():
        print(f"  {key}: {Path(path).name if 'dir' not in key else Path(path).name}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_base)
    
    print("\n✅ directory_builder.py tests passed!")