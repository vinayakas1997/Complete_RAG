"""
Utils Package
Common utilities for file operations and network handling.
"""

from .file_utils import (
    get_file_stem,
    get_file_extension,
    sanitize_filename,
    generate_folder_name,
    ensure_directory,
    get_unique_filename,
    is_supported_image,
    is_pdf,
    get_file_size,
    format_file_size,
    get_timestamp_string,
    list_files_in_directory,
)

from .network_utils import (
    configure_proxy_bypass,
    test_connection,
    check_ollama_running,
    list_ollama_models,
    verify_model_exists,
    get_local_ip,
    print_connection_diagnostics,
)

__all__ = [
    # File utils
    'get_file_stem',
    'get_file_extension',
    'sanitize_filename',
    'generate_folder_name',
    'ensure_directory',
    'get_unique_filename',
    'is_supported_image',
    'is_pdf',
    'get_file_size',
    'format_file_size',
    'get_timestamp_string',
    'list_files_in_directory',
    # Network utils
    'configure_proxy_bypass',
    'test_connection',
    'check_ollama_running',
    'list_ollama_models',
    'verify_model_exists',
    'get_local_ip',
    'print_connection_diagnostics',
]