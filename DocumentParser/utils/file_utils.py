"""
File Utilities Module
Handles file naming, path operations, and directory management.
Reusable across all modules - NO OCR logic here, pure file operations only.
"""

from pathlib import Path
from typing import Optional, Union
from datetime import datetime
import uuid


def get_file_stem(filepath: Union[str, Path]) -> str:
    """
    Get filename without extension.
    
    Args:
        filepath: Path to file
        
    Returns:
        str: Filename without extension
        
    Example:
        >>> get_file_stem("report.pdf")
        'report'
        >>> get_file_stem("/path/to/document.png")
        'document'
    """
    return Path(filepath).stem


def get_file_extension(filepath: Union[str, Path]) -> str:
    """
    Get file extension (lowercase, without dot).
    
    Args:
        filepath: Path to file
        
    Returns:
        str: Extension without dot
        
    Example:
        >>> get_file_extension("document.PDF")
        'pdf'
    """
    return Path(filepath).suffix.lower().lstrip('.')


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be filesystem-safe.
    Removes/replaces problematic characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
        
    Example:
        >>> sanitize_filename("my file: test/2024")
        'my_file_test_2024'
    """
    # Characters to replace with underscore
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Replace multiple underscores with single
    while '__' in sanitized:
        sanitized = sanitized.replace('__', '_')
    
    return sanitized


def generate_folder_name(
    filepath: Union[str, Path],
    strategy: str = "stem",
    timestamp: bool = False
) -> str:
    """
    Generate output folder name based on input file.
    
    Args:
        filepath: Input file path
        strategy: Naming strategy - "stem", "full", "uuid", "timestamp"
        timestamp: Add timestamp suffix
        
    Returns:
        str: Generated folder name
        
    Example:
        >>> generate_folder_name("report.pdf", strategy="stem")
        'report'
        >>> generate_folder_name("report.pdf", strategy="stem", timestamp=True)
        'report_20251217_143052'
    """
    path = Path(filepath)
    
    if strategy == "stem":
        base_name = path.stem
    elif strategy == "full":
        base_name = path.name
    elif strategy == "uuid":
        base_name = f"{path.stem}_{str(uuid.uuid4())[:8]}"
    elif strategy == "timestamp":
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{path.stem}_{ts}"
        return sanitize_filename(base_name)
    else:
        base_name = path.stem
    
    # Add timestamp if requested
    if timestamp and strategy != "timestamp":
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{base_name}_{ts}"
    
    return sanitize_filename(base_name)


def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
        
    Returns:
        Path: Path object of the directory
        
    Example:
        >>> ensure_directory("output/test")
        PosixPath('output/test')
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_unique_filename(
    directory: Union[str, Path],
    base_name: str,
    extension: str = ""
) -> Path:
    """
    Get unique filename by adding suffix if file exists.
    
    Args:
        directory: Target directory
        base_name: Base filename
        extension: File extension (with or without dot)
        
    Returns:
        Path: Unique file path
        
    Example:
        >>> get_unique_filename("output", "report", ".json")
        PosixPath('output/report.json')
        # If report.json exists:
        PosixPath('output/report_1.json')
    """
    directory = Path(directory)
    
    # Ensure extension has dot
    if extension and not extension.startswith('.'):
        extension = f'.{extension}'
    
    # Try original name first
    filepath = directory / f"{base_name}{extension}"
    
    if not filepath.exists():
        return filepath
    
    # Add suffix if exists
    counter = 1
    while True:
        filepath = directory / f"{base_name}_{counter}{extension}"
        if not filepath.exists():
            return filepath
        counter += 1


def is_supported_image(filepath: Union[str, Path]) -> bool:
    """
    Check if file is a supported image format.
    
    Args:
        filepath: File path to check
        
    Returns:
        bool: True if supported image format
        
    Example:
        >>> is_supported_image("photo.jpg")
        True
        >>> is_supported_image("document.pdf")
        False
    """
    supported_formats = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp'}
    extension = get_file_extension(filepath)
    return extension in supported_formats


def is_pdf(filepath: Union[str, Path]) -> bool:
    """
    Check if file is a PDF.
    
    Args:
        filepath: File path to check
        
    Returns:
        bool: True if PDF file
        
    Example:
        >>> is_pdf("document.pdf")
        True
    """
    return get_file_extension(filepath) == 'pdf'


def get_file_size(filepath: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        filepath: File path
        
    Returns:
        int: File size in bytes
        
    Example:
        >>> get_file_size("document.pdf")
        245678
    """
    return Path(filepath).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
        
    Example:
        >>> format_file_size(1024)
        '1.00 KB'
        >>> format_file_size(1048576)
        '1.00 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_timestamp_string(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp as string.
    
    Args:
        format_str: strftime format string
        
    Returns:
        str: Formatted timestamp
        
    Example:
        >>> get_timestamp_string()
        '20251217_143052'
    """
    return datetime.now().strftime(format_str)


def list_files_in_directory(
    directory: Union[str, Path],
    extensions: Optional[list] = None,
    recursive: bool = False
) -> list:
    """
    List files in directory with optional filtering.
    
    Args:
        directory: Directory to search
        extensions: List of extensions to filter (e.g., ['pdf', 'png'])
        recursive: Search subdirectories
        
    Returns:
        list: List of Path objects
        
    Example:
        >>> list_files_in_directory("input", extensions=['pdf', 'png'])
        [PosixPath('input/doc1.pdf'), PosixPath('input/img1.png')]
    """
    directory = Path(directory)
    
    if not directory.exists():
        return []
    
    if recursive:
        pattern = '**/*'
    else:
        pattern = '*'
    
    files = []
    for item in directory.glob(pattern):
        if item.is_file():
            if extensions:
                if get_file_extension(item) in extensions:
                    files.append(item)
            else:
                files.append(item)
    
    return sorted(files)


if __name__ == "__main__":
    # Quick tests
    print("Testing file_utils...")
    
    print(f"get_file_stem('report.pdf'): {get_file_stem('report.pdf')}")
    print(f"get_file_extension('Document.PDF'): {get_file_extension('Document.PDF')}")
    print(f"sanitize_filename('my: file/test'): {sanitize_filename('my: file/test')}")
    print(f"generate_folder_name('report.pdf', 'stem'): {generate_folder_name('report.pdf', 'stem')}")
    print(f"is_supported_image('photo.jpg'): {is_supported_image('photo.jpg')}")
    print(f"is_pdf('document.pdf'): {is_pdf('document.pdf')}")
    print(f"format_file_size(1048576): {format_file_size(1048576)}")
    print(f"get_timestamp_string(): {get_timestamp_string()}")
    
    print("\n✅ file_utils.py tests passed!")