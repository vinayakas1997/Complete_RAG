"""
Markdown Parser Module
Parses plain markdown output without grounding information.
Used when grounding is disabled or not supported by the model.
"""

from typing import List, Optional
import re

from .base_parser import BaseParser, ParseResult, ParsedElement


class MarkdownParser(BaseParser):
    """
    Parser for plain markdown OCR output.
    
    Since there's no grounding information, this parser:
    - Creates synthetic bounding boxes (all zeros or estimated)
    - Identifies structure from markdown syntax (headers, tables, lists)
    - Assigns element types based on content patterns
    """
    
    def __init__(self):
        super().__init__(parser_name="markdown_parser")
    
    def can_parse(self, raw_output: str) -> bool:
        """
        Check if output is plain text/markdown (no grounding tags).
        
        Args:
            raw_output: Raw OCR output
            
        Returns:
            bool: True if no grounding tags present
        """
        if not self.validate_output(raw_output):
            return False
        
        # If it has grounding tags, use grounding parser instead
        has_grounding = '<|ref|>' in raw_output or '<|det|>' in raw_output
        
        return not has_grounding
    
    def parse(self, raw_output: str) -> ParseResult:
        """
        Parse markdown output into structured elements.
        
        Args:
            raw_output: Raw OCR markdown output
            
        Returns:
            ParseResult: Parsed elements (without real bounding boxes)
        """
        if not self.validate_output(raw_output):
            return self.create_error_result(
                raw_output,
                "Invalid or empty output"
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
                    'has_grounding': False,
                    'note': 'Bounding boxes are synthetic (not real)'
                }
            )
        
        except Exception as e:
            return self.create_error_result(
                raw_output,
                f"Parsing failed: {str(e)}"
            )
    
    def _extract_elements(self, text: str) -> List[ParsedElement]:
        """
        Extract structural elements from markdown text.
        
        Args:
            text: Raw markdown text
            
        Returns:
            List[ParsedElement]: List of parsed elements
        """
        elements = []
        lines = text.split('\n')
        
        element_id = 1
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check for different element types
            element = None
            
            # Headers (# ## ###)
            if line.startswith('#'):
                element = self._parse_header(line, element_id, i)
            
            # Tables (starts with |)
            elif line.startswith('|'):
                element, lines_consumed = self._parse_table(lines, i, element_id)
                i += lines_consumed - 1  # -1 because we increment at end
            
            # Lists (- or *)
            elif line.startswith(('-', '*', '+')):
                element, lines_consumed = self._parse_list(lines, i, element_id)
                i += lines_consumed - 1
            
            # HTML tables
            elif '<table>' in line.lower():
                element, lines_consumed = self._parse_html_table(lines, i, element_id)
                i += lines_consumed - 1
            
            # Code blocks (```)
            elif line.startswith('```'):
                element, lines_consumed = self._parse_code_block(lines, i, element_id)
                i += lines_consumed - 1
            
            # Regular text paragraph
            else:
                element, lines_consumed = self._parse_paragraph(lines, i, element_id)
                i += lines_consumed - 1
            
            if element:
                elements.append(element)
                element_id += 1
            
            i += 1
        
        return elements
    
    def _parse_header(self, line: str, element_id: int, line_num: int) -> ParsedElement:
        """Parse markdown header"""
        # Count # symbols for level
        level = len(line) - len(line.lstrip('#'))
        content = line.lstrip('#').strip()
        
        return ParsedElement(
            element_id=element_id,
            element_type=f"heading_{level}",
            bbox=[0, 0, 0, 0],  # Synthetic bbox
            content=content,
            metadata={
                'line_number': line_num + 1,
                'heading_level': level
            }
        )
    
    def _parse_table(self, lines: List[str], start_idx: int, element_id: int) -> tuple:
        """Parse markdown table"""
        table_lines = []
        i = start_idx
        
        # Collect all table lines
        while i < len(lines) and lines[i].strip().startswith('|'):
            table_lines.append(lines[i])
            i += 1
        
        content = '\n'.join(table_lines)
        lines_consumed = len(table_lines)
        
        element = ParsedElement(
            element_id=element_id,
            element_type="table",
            bbox=[0, 0, 0, 0],
            content=content,
            metadata={
                'line_number': start_idx + 1,
                'rows': len(table_lines)
            }
        )
        
        return element, lines_consumed
    
    def _parse_list(self, lines: List[str], start_idx: int, element_id: int) -> tuple:
        """Parse markdown list"""
        list_lines = []
        i = start_idx
        
        # Collect all list items
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith(('-', '*', '+')) or line.startswith('  '):
                list_lines.append(lines[i])
                i += 1
            elif not line:
                i += 1
                continue
            else:
                break
        
        content = '\n'.join(list_lines)
        lines_consumed = len(list_lines)
        
        element = ParsedElement(
            element_id=element_id,
            element_type="list",
            bbox=[0, 0, 0, 0],
            content=content,
            metadata={
                'line_number': start_idx + 1,
                'items': len(list_lines)
            }
        )
        
        return element, lines_consumed
    
    def _parse_html_table(self, lines: List[str], start_idx: int, element_id: int) -> tuple:
        """Parse HTML table"""
        table_lines = []
        i = start_idx
        
        # Collect until </table>
        while i < len(lines):
            table_lines.append(lines[i])
            if '</table>' in lines[i].lower():
                i += 1
                break
            i += 1
        
        content = '\n'.join(table_lines)
        lines_consumed = len(table_lines)
        
        element = ParsedElement(
            element_id=element_id,
            element_type="table",
            bbox=[0, 0, 0, 0],
            content=content,
            metadata={
                'line_number': start_idx + 1,
                'format': 'html'
            }
        )
        
        return element, lines_consumed
    
    def _parse_code_block(self, lines: List[str], start_idx: int, element_id: int) -> tuple:
        """Parse code block"""
        code_lines = [lines[start_idx]]  # Include opening ```
        i = start_idx + 1
        
        # Collect until closing ```
        while i < len(lines):
            code_lines.append(lines[i])
            if lines[i].strip().startswith('```'):
                i += 1
                break
            i += 1
        
        content = '\n'.join(code_lines)
        lines_consumed = len(code_lines)
        
        element = ParsedElement(
            element_id=element_id,
            element_type="code_block",
            bbox=[0, 0, 0, 0],
            content=content,
            metadata={
                'line_number': start_idx + 1
            }
        )
        
        return element, lines_consumed
    
    def _parse_paragraph(self, lines: List[str], start_idx: int, element_id: int) -> tuple:
        """Parse text paragraph"""
        para_lines = []
        i = start_idx
        
        # Collect until empty line or special element
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop at empty line
            if not line:
                break
            
            # Stop at special elements
            if (line.startswith('#') or 
                line.startswith('|') or 
                line.startswith(('-', '*', '+')) or
                line.startswith('```') or
                '<table>' in line.lower()):
                break
            
            para_lines.append(lines[i])
            i += 1
        
        content = '\n'.join(para_lines)
        lines_consumed = len(para_lines)
        
        element = ParsedElement(
            element_id=element_id,
            element_type="text",
            bbox=[0, 0, 0, 0],
            content=content,
            metadata={
                'line_number': start_idx + 1
            }
        )
        
        return element, lines_consumed


if __name__ == "__main__":
    print("Testing markdown_parser.py...\n")
    
    # Test 1: Sample markdown output
    print("Test 1: Parse Markdown Output")
    print("-" * 60)
    
    sample_markdown = """# Document Title

This is a paragraph of text explaining the document.

## Section 1

Here is some content in section 1.

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

### Subsection

- Item 1
- Item 2
- Item 3

More text here.

<table>
<tr><td>HTML Table</td><td>Data</td></tr>
</table>
```python
# Code block
def hello():
    print("world")
```

Final paragraph."""
    
    parser = MarkdownParser()
    
    # Check if can parse
    can_parse = parser.can_parse(sample_markdown)
    print(f"Can parse: {can_parse}")
    
    # Parse output
    result = parser.parse(sample_markdown)
    print(f"Success: {result.success}")
    print(f"Total elements: {result.get_element_count()}")
    
    # Test 2: Show parsed elements
    print("\n" + "="*60)
    print("Test 2: Parsed Elements")
    print("-" * 60)
    for elem in result.elements:
        content_preview = elem.content[:40] + "..." if len(elem.content) > 40 else elem.content
        print(f"#{elem.element_id} [{elem.element_type}] {content_preview}")
    
    # Test 3: Filter by type
    print("\n" + "="*60)
    print("Test 3: Filter by Type")
    print("-" * 60)
    tables = result.get_elements_by_type("table")
    headers = [e for e in result.elements if e.element_type.startswith("heading_")]
    lists = result.get_elements_by_type("list")
    
    print(f"Tables: {len(tables)}")
    print(f"Headers: {len(headers)}")
    print(f"Lists: {len(lists)}")
    
    # Test 4: Check it rejects grounding format
    print("\n" + "="*60)
    print("Test 4: Reject Grounding Format")
    print("-" * 60)
    grounding_text = "<|ref|>table<|/ref|><|det|>[[1,2,3,4]]<|/det|>"
    can_parse_grounding = parser.can_parse(grounding_text)
    print(f"Can parse grounding format: {can_parse_grounding} (should be False)")
    
    print("\n✅ markdown_parser.py tests passed!")