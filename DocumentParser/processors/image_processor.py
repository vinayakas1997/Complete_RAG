"""
Image Processor Module
Handles image preprocessing before OCR.
Includes resizing, format conversion, and optional enhancements.
"""

from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageEnhance
import io


class ImageProcessor:
    """
    Image preprocessing for OCR.
    Prepares images for optimal OCR results.
    """
    
    def __init__(
        self,
        max_dimension: Optional[int] = None,
        maintain_aspect_ratio: bool = True,
        convert_to_rgb: bool = True
    ):
        """
        Initialize image processor.
        
        Args:
            max_dimension: Maximum width or height (None = no resize)
            maintain_aspect_ratio: Keep aspect ratio when resizing
            convert_to_rgb: Convert all images to RGB format
        """
        self.max_dimension = max_dimension
        self.maintain_aspect_ratio = maintain_aspect_ratio
        self.convert_to_rgb = convert_to_rgb
    
    def process_image(
        self,
        image_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Process image with configured settings.
        
        Args:
            image_path: Path to input image
            output_path: Path to save processed image (None = overwrite)
            
        Returns:
            str: Path to processed image
            
        Example:
            >>> processor = ImageProcessor(max_dimension=2048)
            >>> output = processor.process_image("large_image.jpg")
            >>> print(output)
            'large_image.jpg'  # Resized in place
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        img = Image.open(image_path)
        
        # Apply processing
        img = self._preprocess(img)
        

        ## code rabbit 
        with Image.open(image_path) as img:
            #apply processing
            processed_img = self._preprocess(img) 

            # Determine output path
            if output_path is None:
                output_path = image_path
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

            processed_img.save(output_path, format='PNG')
        # # Save processed image
        # img.save(output_path, format='PNG')
        
        return str(output_path)
    
    def _preprocess(self, img: Image.Image) -> Image.Image:
        """
        Apply preprocessing steps to image.
        
        Args:
            img: PIL Image
            
        Returns:
            Image.Image: Processed image
        """
        # Convert to RGB if needed
        if self.convert_to_rgb and img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if needed
        if self.max_dimension:
            img = self._resize_image(img)
        
        return img
    
    def _resize_image(self, img: Image.Image) -> Image.Image:
        """
        Resize image to fit within max dimension.
        
        Args:
            img: PIL Image
            
        Returns:
            Image.Image: Resized image
        """
        width, height = img.size
        
        # Check if resize needed
        if width <= self.max_dimension and height <= self.max_dimension:
            return img
        
        if self.maintain_aspect_ratio:
            # Calculate new size maintaining aspect ratio
            if width > height:
                new_width = self.max_dimension
                new_height = int(height * (self.max_dimension / width))
            else:
                new_height = self.max_dimension
                new_width = int(width * (self.max_dimension / height))
        else:
            # Fixed size (may distort)
            new_width = self.max_dimension
            new_height = self.max_dimension
        
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get image metadata and information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Image information
            
        Example:
            >>> processor = ImageProcessor()
            >>> info = processor.get_image_info("photo.jpg")
            >>> print(info)
            {'width': 1920, 'height': 1080, 'format': 'JPEG', ...}
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        img = Image.open(image_path)
        
        info = {
            'filename': image_path.name,
            'filepath': str(image_path.absolute()),
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode,
            'size_bytes': image_path.stat().st_size
        }
        
        img.close()
        return info
    
    def enhance_image(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        contrast: float = 1.0,
        brightness: float = 1.0,
        sharpness: float = 1.0
    ) -> str:
        """
        Enhance image quality for better OCR.
        
        Args:
            image_path: Path to input image
            output_path: Path to save enhanced image (None = overwrite)
            contrast: Contrast factor (1.0 = no change, >1 = more contrast)
            brightness: Brightness factor (1.0 = no change, >1 = brighter)
            sharpness: Sharpness factor (1.0 = no change, >1 = sharper)
            
        Returns:
            str: Path to enhanced image
            
        Example:
            >>> processor = ImageProcessor()
            >>> output = processor.enhance_image(
            ...     "blurry.jpg",
            ...     contrast=1.5,
            ...     sharpness=2.0
            ... )
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        img = Image.open(image_path)
        
        # Apply enhancements
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
        
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness)
        
        # Determine output path
        if output_path is None:
            output_path = image_path
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save enhanced image
        img.save(output_path, format='PNG')
        
        return str(output_path)
    
    def convert_format(
        self,
        image_path: str,
        output_format: str = 'PNG',
        output_path: Optional[str] = None
    ) -> str:
        """
        Convert image to different format.
        
        Args:
            image_path: Path to input image
            output_format: Target format (PNG, JPEG, etc.)
            output_path: Path to save converted image
            
        Returns:
            str: Path to converted image
            
        Example:
            >>> processor = ImageProcessor()
            >>> png = processor.convert_format("photo.jpg", "PNG")
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        img = Image.open(image_path)
        
        # Convert to RGB if saving as JPEG
        if output_format.upper() == 'JPEG' and img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Determine output path
        if output_path is None:
            output_path = image_path.with_suffix(f'.{output_format.lower()}')
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save in new format
        img.save(output_path, format=output_format.upper())
        
        return str(output_path)
    
    def validate_image(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if file is a valid image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
            
        Example:
            >>> processor = ImageProcessor()
            >>> is_valid, error = processor.validate_image("photo.jpg")
            >>> if is_valid:
            ...     print("Valid image!")
        """
        image_path = Path(image_path)
        
        # Check file exists
        if not image_path.exists():
            return False, f"File not found: {image_path}"
        
        # Try to open as image
        try:
            img = Image.open(image_path)
            img.verify()  # Verify it's a valid image
            img.close()
            
            # Reopen to check if readable
            img = Image.open(image_path)
            img.load()
            img.close()
            
            return True, None
        
        except Exception as e:
            return False, f"Invalid image: {str(e)}"


if __name__ == "__main__":
    print("Testing image_processor.py...\n")
    
    # Test 1: Create processor
    print("Test 1: Processor Creation")
    print("-" * 60)
    processor = ImageProcessor(max_dimension=2048)
    print(f"Max dimension: {processor.max_dimension}")
    print(f"Maintain aspect ratio: {processor.maintain_aspect_ratio}")
    print(f"Convert to RGB: {processor.convert_to_rgb}")
    
    # Test 2: Create test image
    print("\n" + "="*60)
    print("Test 2: Create Test Image")
    print("-" * 60)
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    test_image = temp_dir / "test.png"
    
    # Create a simple test image
    img = Image.new('RGB', (3000, 2000), color='white')
    img.save(test_image)
    print(f"Created test image: {test_image}")
    
    # Test 3: Get image info
    print("\n" + "="*60)
    print("Test 3: Get Image Info")
    print("-" * 60)
    info = processor.get_image_info(str(test_image))
    print(f"Width: {info['width']}")
    print(f"Height: {info['height']}")
    print(f"Format: {info['format']}")
    print(f"Mode: {info['mode']}")
    
    # Test 4: Process image (resize)
    print("\n" + "="*60)
    print("Test 4: Resize Image")
    print("-" * 60)
    output = processor.process_image(str(test_image))
    new_info = processor.get_image_info(output)
    print(f"Original: {info['width']}x{info['height']}")
    print(f"Resized: {new_info['width']}x{new_info['height']}")
    
    # Test 5: Validate image
    print("\n" + "="*60)
    print("Test 5: Validate Image")
    print("-" * 60)
    is_valid, error = processor.validate_image(str(test_image))
    print(f"Valid: {is_valid}")
    print(f"Error: {error}")
    
    # Test 6: Invalid file
    print("\n" + "="*60)
    print("Test 6: Invalid Image")
    print("-" * 60)
    is_valid, error = processor.validate_image("nonexistent.jpg")
    print(f"Valid: {is_valid}")
    print(f"Error: {error}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    
    print("\n✅ image_processor.py tests passed!")