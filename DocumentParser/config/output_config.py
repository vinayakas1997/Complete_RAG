"""
Output Configuration Module
Manages output directory structure and file organization.
Handles multi-page documents and smart folder naming.
"""

from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class OutputConfig:
    """
    Configuration for output directory management.
    
    Controls how extracted data is organized and saved.
    """
    
    # Base output directory
    output_base_dir: str = "output"
    
    # Folder naming strategy
    auto_create_folder: bool = True  # Create folder from filename
    folder_naming: str = "stem"      # stem, full, uuid, timestamp
    add_timestamp: bool = False      # Add timestamp to folder name
    
    # Multi-page settings
    split_pages: bool = True         # Create separate folders for pages
    pages_subfolder: str = "pages"   # Name of pages subfolder
    page_naming_format: str = "page_{num:03d}"  # e.g., page_001, page_002
    
    # What to save per page
    save_per_page: Dict[str, bool] = field(default_factory=lambda: {
        "raw_output": True,          # Raw OCR text output
        "grounding_json": True,      # Bounding box data
        "annotated_image": False,    # Image with bounding boxes
        "original_image": False,     # Extracted page image
        "markdown": True             # Markdown format
    })
    
    # Combined outputs (for multi-page documents)
    create_combined: bool = True     # Merge all pages
    combined_subfolder: str = "combined"
    combined_formats: list = field(default_factory=lambda: ["markdown", "json"])
    
    # Visualization settings
    save_visualizations: bool = False  # Save annotated images
    visualization_subfolder: str = "visualizations"
    
    # Metadata
    save_metadata: bool = True       # Save extraction metadata
    metadata_filename: str = "metadata.json"
    
    # Cleanup
    cleanup_intermediates: bool = False  # Remove temporary files


def get_default_output_config() -> OutputConfig:
    """
    Get default output configuration.
    
    Returns:
        OutputConfig: Default configuration
        
    Example:
        >>> config = get_default_output_config()
        >>> print(config.output_base_dir)
        'output'
    """
    return OutputConfig()


def get_minimal_output_config() -> OutputConfig:
    """
    Get minimal output configuration (saves less files).
    Good for batch processing to save disk space.
    
    Returns:
        OutputConfig: Minimal configuration
        
    Example:
        >>> config = get_minimal_output_config()
        >>> print(config.save_per_page["raw_output"])
        False
    """
    return OutputConfig(
        save_per_page={
            "raw_output": False,
            "grounding_json": True,
            "annotated_image": False,
            "original_image": False,
            "markdown": True
        },
        save_visualizations=False,
        cleanup_intermediates=True
    )


def get_full_output_config() -> OutputConfig:
    """
    Get full output configuration (saves everything).
    Good for analysis and debugging.
    
    Returns:
        OutputConfig: Full configuration
        
    Example:
        >>> config = get_full_output_config()
        >>> print(config.save_per_page["annotated_image"])
        True
    """
    return OutputConfig(
        save_per_page={
            "raw_output": True,
            "grounding_json": True,
            "annotated_image": True,
            "original_image": True,
            "markdown": True
        },
        save_visualizations=True,
        cleanup_intermediates=False
    )


def validate_output_config(config: OutputConfig) -> bool:
    """
    Validate output configuration for common issues.
    
    Args:
        config: Output configuration to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If configuration is invalid
        
    Example:
        >>> config = get_default_output_config()
        >>> validate_output_config(config)
        True
    """
    # Check folder naming strategy
    valid_strategies = ["stem", "full", "uuid", "timestamp"]
    if config.folder_naming not in valid_strategies:
        raise ValueError(
            f"Invalid folder_naming: {config.folder_naming}. "
            f"Must be one of: {valid_strategies}"
        )
    
    # Check page naming format
    if "{num" not in config.page_naming_format:
        raise ValueError(
            "page_naming_format must contain {num} placeholder"
        )
    
    # Check combined formats
    valid_formats = ["markdown", "json", "html", "csv"]
    for fmt in config.combined_formats:
        if fmt not in valid_formats:
            raise ValueError(
                f"Invalid combined format: {fmt}. "
                f"Must be one of: {valid_formats}"
            )
    
    return True


def print_output_config(config: OutputConfig):
    """
    Print output configuration in readable format.
    
    Args:
        config: Output configuration
        
    Example:
        >>> config = get_default_output_config()
        >>> print_output_config(config)
        Output Configuration
        ====================
        Base Directory: output
        ...
    """
    print("\nOutput Configuration")
    print("=" * 60)
    print(f"Base Directory: {config.output_base_dir}")
    print(f"Auto Create Folder: {config.auto_create_folder}")
    print(f"Folder Naming: {config.folder_naming}")
    
    print(f"\nMulti-page Settings:")
    print(f"  Split Pages: {config.split_pages}")
    print(f"  Pages Subfolder: {config.pages_subfolder}")
    print(f"  Page Naming: {config.page_naming_format}")
    
    print(f"\nFiles Saved Per Page:")
    for key, value in config.save_per_page.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}")
    
    print(f"\nCombined Output:")
    print(f"  Create Combined: {config.create_combined}")
    print(f"  Formats: {config.combined_formats}")
    
    print(f"\nVisualization:")
    print(f"  Save Visualizations: {config.save_visualizations}")
    
    print(f"\nMetadata:")
    print(f"  Save Metadata: {config.save_metadata}")
    
    print("=" * 60)


if __name__ == "__main__":
    print("Testing output_config.py...\n")
    
    # Test 1: Default config
    print("Default Configuration:")
    print("-" * 60)
    default_config = get_default_output_config()
    print(f"Output dir: {default_config.output_base_dir}")
    print(f"Auto create folder: {default_config.auto_create_folder}")
    
    # Test 2: Minimal config
    print("\n" + "="*60)
    print("Minimal Configuration:")
    print("-" * 60)
    minimal_config = get_minimal_output_config()
    print(f"Save raw output: {minimal_config.save_per_page['raw_output']}")
    print(f"Save grounding: {minimal_config.save_per_page['grounding_json']}")
    
    # Test 3: Full config
    print("\n" + "="*60)
    print("Full Configuration:")
    print("-" * 60)
    full_config = get_full_output_config()
    print(f"Save annotated: {full_config.save_per_page['annotated_image']}")
    print(f"Save visualizations: {full_config.save_visualizations}")
    
    # Test 4: Validation
    print("\n" + "="*60)
    try:
        validate_output_config(default_config)
        print("✓ Default config is valid")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")
    
    # Test 5: Print config
    print_output_config(default_config)
    
    print("\n✅ output_config.py tests passed!")