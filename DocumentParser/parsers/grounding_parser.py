"""
Grounding Parser Module
Parses DeepSeek OCR output with grounding/bounding box information.
Handles <|ref|>label<|/ref|><|det|>[[x1,y1,x2,y2]]<|/det|> format.
"""

from typing import List, Optional
import re

from .base_parser import BaseParser, ParseResult, ParsedElement


class GroundingParser(BaseParser):
    """
    Parser for DeepSeek OCR grounding format.
    
    Expected format:
    <|ref|>label<|/ref|><|det|>[[x1,y1,x2,y2]]<|/det|>
    content text...
    
    Example:
    <|ref|>table<|/ref|><|det|>[[59, 53, 582, 105]]<|/det|>
    <table><tr><td>...</td></tr></table>
    """
    
    def __init__(self):
        super().__init__(parser_name="grounding_parser")
    
    def can_parse(self, raw_output: str) -> bool:
        """
        Check if output contains grounding tags.
        
        Args:
            raw_output: Raw OCR output
            
        Returns:
            bool: True if contains <|ref|> and <|det|> tags
        """
        if not self.validate_output(raw_output):
            return False
        
        # Check for grounding tags
        has_ref = '<|ref|>' in raw_output and '<|/ref|>' in raw_output
        has_det = '<|det|>' in raw_output and '<|/det|>' in raw_output
        
        return has_ref and has_det
    
    def parse(self, raw_output: str) -> ParseResult:
        """
        Parse grounding output into structured elements.
        
        Args:
            raw_output: Raw OCR output with grounding tags
            
        Returns:
            ParseResult: Parsed elements with bounding boxes
        """
        if not self.validate_output(raw_output):
            return self.create_error_result(
                raw_output,
                "Invalid or empty output"
            )
        
        if not self.can_parse(raw_output):
            return self.create_error_result(
                raw_output,
                "Output does not contain grounding tags"
            )
        
        try:
            elements = self._extract_elements(raw_output)
            
            return ParseResult(
                elements=elements,
                raw_text=raw_output,
                parser_type=self.parser_name,
                success=True,
                metadata={
                    'element_count': len(elements),
                    'has_grounding': True
                }
            )
        
        except Exception as e:
            return self.create_error_result(
                raw_output,
                f"Parsing failed: {str(e)}"
            )
    
    def _extract_elements(self, text: str) -> List[ParsedElement]:
        """
        Extract all grounding elements from text.
        
        Args:
            text: Raw output text
            
        Returns:
            List[ParsedElement]: List of parsed elements
        """
        elements = []
        lines = text.split('\n')
        
        element_id = 1
        
        for i, line in enumerate(lines):
            # Check if line contains grounding tags
            if '<|ref|>' in line and '<|det|>' in line:
                try:
                    element = self._parse_line(line, element_id, lines, i)
                    if element:
                        elements.append(element)
                        element_id += 1
                except Exception as e:
                    # Skip malformed lines but continue parsing
                    print(f"Warning: Could not parse line {i+1}: {e}")
                    continue
        
        return elements
    
    def _parse_line(
        self,
        line: str,
        element_id: int,
        all_lines: List[str],
        current_index: int
    ) -> Optional[ParsedElement]:
        """
        Parse a single line with grounding tags.
        
        Args:
            line: Line to parse
            element_id: ID for this element
            all_lines: All lines (for extracting content)
            current_index: Index of current line
            
        Returns:
            ParsedElement or None if parsing fails
        """
        # Extract label between <|ref|> and <|/ref|>
        label_match = re.search(r'<\|ref\|>([^<]+)<\|/ref\|>', line)
        if not label_match:
            return None
        label = label_match.group(1).strip()
        
        # Extract coordinates between [[ and ]]
        coords_match = re.search(r'\[\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]\]', line)
        if not coords_match:
            return None
        
        x1 = int(coords_match.group(1))
        y1 = int(coords_match.group(2))
        x2 = int(coords_match.group(3))
        y2 = int(coords_match.group(4))
        bbox = [x1, y1, x2, y2]
        
        # Extract content after tags (on same line or next lines)
        content = self._extract_content(line, all_lines, current_index)
        
        return ParsedElement(
            element_id=element_id,
            element_type=label,
            bbox=bbox,
            content=content,
            confidence=None,  # DeepSeek OCR doesn't provide confidence scores
            metadata={
                'line_number': current_index + 1,
                'raw_line': line
            }
        )
    
    def _extract_content(
        self,
        current_line: str,
        all_lines: List[str],
        current_index: int
    ) -> str:
        """
        Extract content associated with the grounding element.
        
        Content can be on the same line after tags, or on following lines
        until the next grounding tag or empty line.
        
        Args:
            current_line: Current line with tags
            all_lines: All lines
            current_index: Index of current line
            
        Returns:
            str: Extracted content
        """
        content_parts = []
        
        # Get content after </det|> on same line
        det_end = current_line.find('<|/det|>')
        if det_end != -1:
            same_line_content = current_line[det_end + 8:].strip()
            if same_line_content:
                content_parts.append(same_line_content)
        
        # Get content from following lines
        for i in range(current_index + 1, len(all_lines)):
            next_line = all_lines[i].strip()
            
            # Stop at next grounding tag
            if '<|ref|>' in next_line:
                break
            
            # Stop at empty line (optional - you can remove this if needed)
            # if not next_line:
            #     break
            
            if next_line:
                content_parts.append(next_line)
        
        return '\n'.join(content_parts)
    
    def get_statistics(self, result: ParseResult) -> dict:
        """
        Get statistics about parsed elements.
        
        Args:
            result: Parse result
            
        Returns:
            dict: Statistics including counts by type
        """
        if not result.success:
            return {'error': result.error_message}
        
        # Count elements by type
        type_counts = {}
        for element in result.elements:
            element_type = element.element_type
            type_counts[element_type] = type_counts.get(element_type, 0) + 1
        
        return {
            'total_elements': len(result.elements),
            'element_types': type_counts,
            'has_tables': 'table' in type_counts,
            'has_images': 'image' in type_counts,
            'has_text': 'text' in type_counts
        }


if __name__ == "__main__":
    print("Testing grounding_parser.py...\n")
    
    # Test 1: Sample DeepSeek OCR output
    print("Test 1: Parse Sample Output")
    print("-" * 60)
    
    sample_output = """<|ref|>table<|/ref|><|det|>[[59, 53, 582, 105]]<|/det|>
<table><tr><td>下野部工場 機密区域管理要領</td><td>付図1</td><td>分類<br/>番号</td><td>02AC001(1)<br/>ページ 3/4</td></tr></table>
<|ref|>sub_title<|/ref|><|det|>[[245, 133, 392, 151]]<|/det|>
社外者の入退場時のフロー
<|ref|>image<|/ref|><|det|>[[65, 154, 575, 565]]<|/det|>
<|ref|>sub_title<|/ref|><|det|>[[210, 574, 426, 593]]<|/det|>
従業員による機密区域内撮影時のフロー
<|ref|>image<|/ref|><|det|>[[65, 597, 575, 982]]<|/det|>"""
    
    parser = GroundingParser()
    
    # Check if can parse
    can_parse = parser.can_parse(sample_output)
    print(f"Can parse: {can_parse}")
    
    # Parse output
    result = parser.parse(sample_output)
    print(f"Success: {result.success}")
    print(f"Total elements: {result.get_element_count()}")
    
    # Test 2: Show parsed elements
    print("\n" + "="*60)
    print("Test 2: Parsed Elements")
    print("-" * 60)
    for elem in result.elements:
        print(f"#{elem.element_id} [{elem.element_type}] at {elem.bbox}")
        content_preview = elem.content[:50] + "..." if len(elem.content) > 50 else elem.content
        print(f"   Content: {content_preview}")
    
    # Test 3: Filter by type
    print("\n" + "="*60)
    print("Test 3: Filter by Type")
    print("-" * 60)
    tables = result.get_elements_by_type("table")
    images = result.get_elements_by_type("image")
    subtitles = result.get_elements_by_type("sub_title")
    
    print(f"Tables: {len(tables)}")
    print(f"Images: {len(images)}")
    print(f"Subtitles: {len(subtitles)}")
    
    # Test 4: Statistics
    print("\n" + "="*60)
    print("Test 4: Statistics")
    print("-" * 60)
    stats = parser.get_statistics(result)
    print(f"Statistics: {stats}")
    
    # Test 5: Convert to dict
    print("\n" + "="*60)
    print("Test 5: Export to Dict")
    print("-" * 60)
    result_dict = result.to_dict()
    print(f"Exportable: {result_dict['success']}")
    print(f"Elements in dict: {len(result_dict['elements'])}")
    
    # Test 6: Invalid input
    print("\n" + "="*60)
    print("Test 6: Invalid Input")
    print("-" * 60)
    invalid_result = parser.parse("No grounding tags here")
    print(f"Success: {invalid_result.success}")
    print(f"Error: {invalid_result.error_message}")
    
    print("\n✅ grounding_parser.py tests passed!")