# DocumentParser Architecture

## 1. High-Level Design

The **DocumentParser** follows a layered architecture, separating concerns between orchestration, extraction, parsing, and storage.

```mermaid
graph TD
    User([User]) --> |Calls| API[OllamaOCR Facade]
    
    subgraph "Core System"
        API --> Processor[MultiPage Processor]
        Processor --> |Converts| PDF[PDF Processor]
        Processor --> |Extracts| Extractor[Ollama Extractor]
        Processor --> |Parses| Parser[Parsers]
        Processor --> |Saves| Storage[Output Manager]
    end
    
    subgraph "External"
        Extractor --> |HTTP| Ollama[Ollama Service]
    end
    
    Storage --> |Writes| Disk[(File System)]
```

## 2. Key Components

| Component | Responsibility |
|-----------|----------------|
| **OllamaOCR** (`main.py`) | The main entry point and facade. Simplifies API usage. |
| **MultiPageProcessor** | Orchestrates the entire pipeline: handles file conversion, loops through pages, and aggregates results. |
| **OllamaExtractor** | Handles the communication with the Ollama API, managing prompts and retries. |
| **PDFProcessor** | Converts PDF pages into high-quality images for the vision models. |
| **OutputManager** | Handles writing results to disk in various formats (JSON, MD). |

## 3. Detailed Processing Flow

### Document Processing Workflow

This sequence diagram illustrates the lifecycle of a `process_document()` call.

```mermaid
sequenceDiagram
    participant User
    participant OCR as OllamaOCR
    participant MP as MultiPageProcessor
    participant PDF as PDFProcessor
    participant EXT as OllamaExtractor
    participant OM as OutputManager
    participant VIZ as BBoxVisualizer

    User->>OCR: process(file_path)
    OCR->>MP: process_document(file_path)
    
    alt is PDF
        MP->>PDF: pdf_to_images(file_path)
        PDF-->>MP: [image_paths]
    else is Image
        Note over MP: Use single image path
    end
    
    loop For Each Page
        MP->>MP: Preprocess (Resize to 1024x1024)
        MP->>EXT: extract(resized_image)
        EXT->>EXT: Call Ollama API
        EXT-->>MP: ExtractionResult
        
        MP->>OM: save_page_result()
        
        opt Visualization Enabled
            MP->>VIZ: visualize(original_image, elements)
            VIZ-->>MP: Annotated Image
            MP->>VIZ: create_comparison()
        end
    end
    
    MP->>MP: Create Combined Output (MD/JSON)
    MP->>MP: Generate Metadata
    MP-->>OCR: DocumentResult
    OCR-->>User: DocumentResult
```

### Page Extraction Logic

The extraction process for a single page involves specific preprocessing to optimize for vision models.

```mermaid
flowchart TD
    Start([Start Page Process]) --> Load[Load Image]
    Load --> Resize[Resize to 1024x1024]
    
    subgraph Extraction
        Resize --> CallModel[Call Ollama Model]
        CallModel --> RawOutput[Raw Text Output]
        RawOutput --> Parse[Parse Grounding Tags]
        Parse --> Elements[Structured Elements]
    end
    
    Elements --> Save[Save JSON/Text]
    Elements --> Viz[Visualize BBoxes]
    
    Viz --> Copy[Copy Resized Image as 'Original']
    Copy --> Draw[Draw Boxes on Image]
    Draw --> Compare[Create Comparison View]
    
    Compare --> Finish([End Page Process])
```

## 4. Class Hierarchy

```mermaid
classDiagram
    class OllamaOCR {
        +config: OCRConfig
        +process(file_path)
        +process_batch(files)
    }

    class MultiPageProcessor {
        +process_document(file_path)
        -_process_page(image_path)
        -_create_combined_output()
    }

    class BaseExtractor {
        <<Abstract>>
        +extract(image_path)
        +validate_config()
    }

    class OllamaExtractor {
        +extract(image_path)
    }

    OllamaOCR --> MultiPageProcessor
    MultiPageProcessor --> BaseExtractor
    BaseExtractor <|-- OllamaExtractor
```
