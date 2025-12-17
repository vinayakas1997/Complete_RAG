"""
Network Utilities Module
Handles network configuration, proxy bypass, and connection testing.
Reusable across all modules - NO OCR logic here.
"""

import os
import requests
from typing import Optional, Dict
import socket


def configure_proxy_bypass():
    """
    Configure environment to bypass proxy for localhost connections.
    Critical for corporate networks that intercept localhost traffic.
    
    This should be called at the start of the application.
    
    Example:
        >>> configure_proxy_bypass()
        # All subsequent requests to localhost will bypass proxy
    """
    bypass_hosts = 'localhost,127.0.0.1,::1'
    
    # Set various proxy environment variables to empty
    proxy_vars = [
        'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
        'ALL_PROXY', 'all_proxy'
    ]
    
    for var in proxy_vars:
        os.environ[var] = ''
    
    # Set NO_PROXY variables
    os.environ['NO_PROXY'] = bypass_hosts
    os.environ['no_proxy'] = bypass_hosts


def test_connection(
    host: str = "http://localhost:11434",
    timeout: int = 5,
    endpoint: str = "/api/tags"
) -> Dict[str, any]:
    """
    Test connection to Ollama or other service.
    
    Args:
        host: Host URL
        timeout: Connection timeout in seconds
        endpoint: API endpoint to test
        
    Returns:
        dict: {
            'success': bool,
            'status_code': int or None,
            'message': str,
            'data': dict or None
        }
        
    Example:
        >>> result = test_connection()
        >>> if result['success']:
        ...     print("Connected!")
    """
    try:
        url = f"{host}{endpoint}"
        response = requests.get(
            url,
            timeout=timeout,
            proxies={'http': None, 'https': None}
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                return {
                    'success': True,
                    'status_code': 200,
                    'message': 'Connection successful',
                    'data': data
                }
            except:
                return {
                    'success': True,
                    'status_code': 200,
                    'message': 'Connection successful (non-JSON response)',
                    'data': None
                }
        else:
            return {
                'success': False,
                'status_code': response.status_code,
                'message': f'HTTP {response.status_code}: {response.reason}',
                'data': None
            }
            
    except requests.exceptions.ConnectionError as e:
        return {
            'success': False,
            'status_code': None,
            'message': f'Connection failed: {str(e)}',
            'data': None
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'status_code': None,
            'message': f'Connection timeout after {timeout} seconds',
            'data': None
        }
    except Exception as e:
        return {
            'success': False,
            'status_code': None,
            'message': f'Error: {str(e)}',
            'data': None
        }


def check_ollama_running(host: str = "http://localhost:11434") -> bool:
    """
    Quick check if Ollama is running.
    
    Args:
        host: Ollama host URL
        
    Returns:
        bool: True if Ollama is accessible
        
    Example:
        >>> if check_ollama_running():
        ...     print("Ollama is ready!")
    """
    result = test_connection(host)
    return result['success']


def list_ollama_models(host: str = "http://localhost:11434") -> Optional[list]:
    """
    Get list of available Ollama models.
    
    Args:
        host: Ollama host URL
        
    Returns:
        list: List of model names, or None if failed
        
    Example:
        >>> models = list_ollama_models()
        >>> print(models)
        ['deepseek-ocr:3b', 'llama-vision:7b', ...]
    """
    result = test_connection(host, endpoint="/api/tags")
    
    if result['success'] and result['data']:
        try:
            models = result['data'].get('models', [])
            return [model['name'] for model in models]
        except:
            return None
    
    return None


def verify_model_exists(
    model_name: str,
    host: str = "http://localhost:11434"
) -> bool:
    """
    Check if a specific model is available in Ollama.
    
    Args:
        model_name: Name of the model to check
        host: Ollama host URL
        
    Returns:
        bool: True if model exists
        
    Example:
        >>> if verify_model_exists("deepseek-ocr:3b"):
        ...     print("Model is available!")
    """
    models = list_ollama_models(host)
    
    if models is None:
        return False
    
    return model_name in models


def get_local_ip() -> str:
    """
    Get local machine IP address.
    
    Returns:
        str: Local IP address
        
    Example:
        >>> get_local_ip()
        '192.168.1.100'
    """
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def print_connection_diagnostics(host: str = "http://localhost:11434"):
    """
    Print detailed connection diagnostics for troubleshooting.
    
    Args:
        host: Host to test
        
    Example:
        >>> print_connection_diagnostics()
        Testing connection to: http://localhost:11434
        ✓ Connection successful
        ✓ Available models: ['deepseek-ocr:3b', ...]
    """
    print(f"\nConnection Diagnostics")
    print("=" * 60)
    print(f"Testing connection to: {host}")
    print(f"Local IP: {get_local_ip()}")
    print()
    
    # Test basic connection
    result = test_connection(host)
    
    if result['success']:
        print(f"✓ Connection successful")
        print(f"  Status: {result['status_code']}")
        
        # List models
        models = list_ollama_models(host)
        if models:
            print(f"✓ Available models ({len(models)}):")
            for model in models[:5]:  # Show first 5
                print(f"  - {model}")
            if len(models) > 5:
                print(f"  ... and {len(models) - 5} more")
        else:
            print("⚠ Could not retrieve model list")
    else:
        print(f"✗ Connection failed")
        print(f"  Message: {result['message']}")
        print()
        print("Troubleshooting:")
        print("1. Check if Ollama is running: 'ollama serve'")
        print("2. Verify host URL is correct")
        print("3. Check firewall settings")
        print("4. Try: configure_proxy_bypass()")
    
    print("=" * 60)


if __name__ == "__main__":
    # Quick tests
    print("Testing network_utils...")
    
    # Configure proxy bypass
    configure_proxy_bypass()
    print("✓ Proxy bypass configured")
    
    # Test connection
    result = test_connection()
    print(f"✓ Connection test: {result['success']}")
    
    # Print diagnostics
    print_connection_diagnostics()
    
    print("\n✅ network_utils.py tests completed!")