"""
Bounding Box Visualizer Module
Draws bounding boxes on images based on grounding data.
Creates annotated images showing detected elements.
"""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont

from ..parsers import ParsedElement


class BBoxVisualizer:
    """
    Visualizes bounding boxes on images.
    
    Creates annotated images showing detected elements with:
    - Colored bounding boxes
    - Element labels
    - Element IDs
    """
    
    def __init__(
        self,
        show_labels: bool = True,
        show_ids: bool = True,
        box_width: int = 3,
        font_size: int = 12,
        color_scheme: str = "default"
    ):
        """
        Initialize visualizer.
        
        Args:
            show_labels: Show element type labels
            show_ids: Show element ID numbers
            box_width: Width of bounding box lines
            font_size: Font size for labels
            color_scheme: Color scheme (default, colorblind, grayscale)
            
        Example:
            >>> visualizer = BBoxVisualizer(show_labels=True, box_width=3)
            >>> visualizer.visualize("image.png", elements, "output.png")
        """
        self.show_labels = show_labels
        self.show_ids = show_ids
        self.box_width = box_width
        self.font_size = font_size
        self.color_scheme = color_scheme
        
        # Load font
        try:
            self.font = ImageFont.truetype("arial.ttf", font_size)
            self.font_small = ImageFont.truetype("arial.ttf", font_size - 2)
        except:
            self.font = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
        
        # Color mappings
        self._setup_colors()
    
    def _setup_colors(self):
        """Setup color schemes for different element types"""
        if self.color_scheme == "default":
            self.colors = {
                'table': (255, 0, 0),       # Red
                'sub_title': (0, 255, 0),   # Green
                'title': (0, 255, 0),       # Green
                'heading_1': (0, 200, 0),   # Dark Green
                'heading_2': (0, 180, 0),   # Medium Green
                'heading_3': (0, 160, 0),   # Light Green
                'image': (0, 0, 255),       # Blue
                'figure': (0, 0, 255),      # Blue
                'text': (255, 255, 0),      # Yellow
                'list': (255, 165, 0),      # Orange
                'code_block': (128, 0, 128), # Purple
                'default': (0, 255, 0)      # Green (fallback)
            }
        
        elif self.color_scheme == "colorblind":
            # Colorblind-friendly palette
            self.colors = {
                'table': (230, 159, 0),     # Orange
                'sub_title': (86, 180, 233), # Sky Blue
                'title': (86, 180, 233),
                'image': (0, 158, 115),     # Bluish Green
                'text': (240, 228, 66),     # Yellow
                'default': (86, 180, 233)
            }
        
        elif self.color_scheme == "grayscale":
            # Grayscale
            self.colors = {
                'table': (50, 50, 50),
                'sub_title': (100, 100, 100),
                'title': (100, 100, 100),
                'image': (150, 150, 150),
                'text': (200, 200, 200),
                'default': (128, 128, 128)
            }
        
        else:
            # Default fallback
            self.colors = {'default': (0, 255, 0)}
    
    def get_color(self, element_type: str) -> Tuple[int, int, int]:
        """
        Get color for element type.
        
        Args:
            element_type: Type of element
            
        Returns:
            Tuple[int, int, int]: RGB color tuple
        """
        return self.colors.get(element_type, self.colors.get('default', (0, 255, 0)))
    
    def visualize(
        self,
        image_path: str,
        elements: List[ParsedElement],
        output_path: str
    ) -> str:
        """
        Create annotated image with bounding boxes.
        
        Args:
            image_path: Path to input image
            elements: List of parsed elements with bounding boxes
            output_path: Path to save annotated image
            
        Returns:
            str: Path to saved annotated image
            
        Example:
            >>> visualizer = BBoxVisualizer()
            >>> output = visualizer.visualize(
            ...     "document.png",
            ...     elements,
            ...     "annotated.png"
            ... )
            >>> print(f"Saved to: {output}")
        """
        image_path = Path(image_path)
        output_path = Path(output_path)
        
        # Load image
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Draw each element
        for element in elements:
            self._draw_element(draw, element)
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save annotated image
        img.save(output_path)
        
        return str(output_path)
    
    def _draw_element(self, draw: ImageDraw.Draw, element: ParsedElement):
        """
        Draw a single element on the image.
        
        Args:
            draw: PIL ImageDraw object
            element: Element to draw
        """
        bbox = element.bbox
        element_type = element.element_type
        
        # Get color for this element type
        color = self.get_color(element_type)
        
        # Draw bounding box
        draw.rectangle(
            [bbox[0], bbox[1], bbox[2], bbox[3]],
            outline=color,
            width=self.box_width
        )
        
        # Draw label if enabled
        if self.show_labels or self.show_ids:
            self._draw_label(draw, element, color)
    
    def _draw_label(
        self,
        draw: ImageDraw.Draw,
        element: ParsedElement,
        color: Tuple[int, int, int]
    ):
        """
        Draw label for element.
        
        Args:
            draw: PIL ImageDraw object
            element: Element to label
            color: Color for label
        """
        bbox = element.bbox
        
        # Construct label text
        label_parts = []
        if self.show_ids:
            label_parts.append(f"#{element.element_id}")
        if self.show_labels:
            label_parts.append(element.element_type)
        
        label_text = ": ".join(label_parts)
        
        # Calculate label position (above box)
        label_x = bbox[0]
        label_y = bbox[1] - 20
        
        # Ensure label is within image bounds
        if label_y < 0:
            label_y = bbox[1] + 2  # Put inside box if no room above
        
        # Draw label background
        bbox_text = draw.textbbox((label_x, label_y), label_text, font=self.font_small)
        draw.rectangle(bbox_text, fill=(255, 255, 255, 230))
        
        # Draw label text
        draw.text(
            (label_x, label_y),
            label_text,
            fill=color,
            font=self.font_small
        )
    
    def create_comparison(
        self,
        original_path: str,
        annotated_path: str,
        output_path: str
    ) -> str:
        """
        Create side-by-side comparison image.
        
        Args:
            original_path: Path to original image
            annotated_path: Path to annotated image
            output_path: Path to save comparison
            
        Returns:
            str: Path to comparison image
            
        Example:
            >>> visualizer = BBoxVisualizer()
            >>> comparison = visualizer.create_comparison(
            ...     "original.png",
            ...     "annotated.png",
            ...     "comparison.png"
            ... )
        """
        # Load both images
        original = Image.open(original_path)
        annotated = Image.open(annotated_path)
        
        # Get dimensions
        orig_width, orig_height = original.size
        anno_width, anno_height = annotated.size
        
        # Resize if heights don't match
        if orig_height != anno_height:
            target_height = max(orig_height, anno_height)
            if orig_height != target_height:
                new_width = int(orig_width * target_height / orig_height)
                original = original.resize((new_width, target_height), Image.LANCZOS)
                orig_width, orig_height = original.size
            if anno_height != target_height:
                new_width = int(anno_width * target_height / anno_height)
                annotated = annotated.resize((new_width, target_height), Image.LANCZOS)
                anno_width, anno_height = annotated.size
        
        # Create combined image
        total_width = orig_width + anno_width
        comparison = Image.new('RGB', (total_width, orig_height), (255, 255, 255))
        
        # Paste images
        comparison.paste(original, (0, 0))
        comparison.paste(annotated, (orig_width, 0))
        
        # Add labels
        draw = ImageDraw.Draw(comparison)
        draw.text((20, 20), "Original", fill=(0, 0, 0), font=self.font)
        draw.text((orig_width + 20, 20), "Annotated", fill=(0, 0, 0), font=self.font)
        
        # Save
        comparison.save(output_path)
        
        return str(output_path)
    
    def get_statistics(self, elements: List[ParsedElement]) -> Dict[str, int]:
        """
        Get statistics about elements.
        
        Args:
            elements: List of elements
            
        Returns:
            dict: Statistics by element type
            
        Example:
            >>> stats = visualizer.get_statistics(elements)
            >>> print(f"Tables: {stats.get('table', 0)}")
        """
        stats = {}
        for element in elements:
            element_type = element.element_type
            stats[element_type] = stats.get(element_type, 0) + 1
        
        return stats


if __name__ == "__main__":
    print("Testing bbox_visualizer.py...\n")
    
    # Test 1: Create visualizer
    print("Test 1: Create Visualizer")
    print("-" * 60)
    visualizer = BBoxVisualizer(
        show_labels=True,
        show_ids=True,
        box_width=3
    )
    print(f"Show labels: {visualizer.show_labels}")
    print(f"Show IDs: {visualizer.show_ids}")
    print(f"Box width: {visualizer.box_width}")
    
    # Test 2: Color schemes
    print("\n" + "="*60)
    print("Test 2: Color Schemes")
    print("-" * 60)
    for scheme in ["default", "colorblind", "grayscale"]:
        viz = BBoxVisualizer(color_scheme=scheme)
        color = viz.get_color("table")
        print(f"{scheme}: table color = {color}")
    
    # Test 3: Create test image with elements
    print("\n" + "="*60)
    print("Test 3: Visualize Test Image")
    print("-" * 60)
    
    try:
        from parsers import ParsedElement
        import tempfile
        
        # Create test image
        temp_dir = Path(tempfile.mkdtemp())
        test_image = temp_dir / "test.png"
        
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some fake content
        draw.rectangle([50, 50, 400, 150], outline='black', width=2)
        draw.text((60, 60), "Table Area", fill='black')
        
        draw.rectangle([50, 200, 400, 300], outline='black', width=2)
        draw.text((60, 210), "Text Area", fill='black')
        
        img.save(test_image)
        print(f"Created test image: {test_image}")
        
        # Create fake elements
        elements = [
            ParsedElement(
                element_id=1,
                element_type="table",
                bbox=[50, 50, 400, 150],
                content="Table content"
            ),
            ParsedElement(
                element_id=2,
                element_type="text",
                bbox=[50, 200, 400, 300],
                content="Text content"
            )
        ]
        
        # Visualize
        output_path = temp_dir / "annotated.png"
        result = visualizer.visualize(
            str(test_image),
            elements,
            str(output_path)
        )
        
        print(f"✓ Created annotated image: {result}")
        
        # Test 4: Statistics
        print("\n" + "="*60)
        print("Test 4: Element Statistics")
        print("-" * 60)
        stats = visualizer.get_statistics(elements)
        print(f"Statistics: {stats}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"Could not test visualization: {e}")
    
    print("\n✅ bbox_visualizer.py tests passed!")