[English](README.md) | [中文](README_CN.md)

# DOCX Master

Professional DOCX intelligent processing agent for academic papers, official documents, and technical documentation.

## Features

- **DOC Format Compatibility** - Automatically convert legacy .doc format to .docx (using Word COM or LibreOffice)
- **Markdown Seamless Conversion** - Support .md/.txt file import, auto-detect LaTeX math formulas, pandoc converts to DOCX
- **Chinese Paper Formatting** - Automatically standardize Chinese academic paper typesetting (GB/T 7713.1-2006)
- **English Paper Formatting** - Support APA, IEEE, ACM and other English paper formats
- **Official Document Formatting** - Compliant with national standards for official document typesetting (GB/T 9704-2012)
- **Margin Management** - Support government documents, academic papers, mirror margins and other standards
- **User Custom Templates** - Support YAML/JSON custom format templates
- **Zero-format Document Processing** - Automatically identify and format plain text/unformatted documents, intelligently detect document structure
- **Smart Heading Recognition** - Support multiple Chinese heading format detection (numbering, colon, context-aware, etc.)
- **Design Preview & Confirmation** - Preview cover page, table of contents, headers/footers and body styles in browser, support online editing
- **Auto Generate Table of Contents** - Use Word TOC field code to auto-generate TOC, including page numbers, level indentation and leader dots
- **Header & Footer Management** - Custom header text, divider line and page number format (Arabic/Roman/Chinese numbers)
- **Paragraph Spacing Control** - Optional "blank line separation between paragraphs", flexible control of body layout style
- **Chinese-English Translation** - Intelligent translation maintaining document structure
- **Math/Chemistry Formula Protection** - Fully preserve OMML (`m:oMath`/`m:oMathPara`), MathType formulas, formula position unchanged after formatting
- **Image Layout Optimization** - Automatically adjust image position and size
- **Table Formatting** - Three-line table style, cell font alignment, table caption detection and formatting, caption and table keep on same page
- **Footnote Formatting** - Footnote/endnote standardization, support academic paper format, auto-detect and format footnote content
- **Custom Format Management** - Provide WEB interface to manage format template configuration, support create, edit, import, export configurations
- **Font Compatibility Management** - Cross-platform font detection and fallback
- **PDF Export** - High-quality PDF output
- **XML Safety Protection** - Prevent DOCX structure corruption

## System Requirements

- Python 3.10+
- Windows 10/11 (Recommended)
- Microsoft Word or LibreOffice (Required for DOC conversion and PDF export)
- Pandoc (Required for Markdown conversion, install: `winget install JohnMacFarlane.Pandoc`)

## Quick Start

### 1. Install Dependencies

```bash
# Windows
install_requirements.bat

# Or manual installation
pip install -r requirements.txt
```

### 2. Usage

1. Place DOCX files in `workspace/input/`
2. Run Agent, select processing options as prompted
3. Confirm in browser preview interface:
   - Cover page design (preserve or redesign)
   - Table of contents configuration (auto-generate, heading styles, max level)
   - Header/footer settings (text, font, alignment, page number format)
   - Body styles (font, size, line spacing, indentation)
   - Paragraph spacing (whether to use blank line separation)
4. After confirmation, system automatically completes format standardization
5. After processing, files are located in `workspace/output/`
6. In Word, press `Ctrl+A` then `F9` to update fields and generate TOC page numbers

## Project Structure

```
doc-from-master/
├── AGENT.md                    # Agent configuration file
├── SKILLS/                     # Skill modules
│   ├── doc-compatibility/      # DOC format compatibility (.doc → .docx)
│   ├── markdown-converter/     # Markdown conversion (.md/.txt → .docx)
│   ├── docx-parser/            # DOCX structure parsing (with cover/TOC detection)
│   ├── xml-safety/             # XML safety validation
│   ├── formula-protection/     # Math formula protection
│   ├── template-engine/        # Template management
│   ├── font-manager/           # Font compatibility management
│   ├── format-normalizer/      # Format standardization (formatted documents)
│   ├── zero-format-normalizer/ # Zero-format standardization (plain text/unformatted)
│   ├── table-processor/        # Table formatting (three-line/caption/cell format)
│   ├── footnote-processor/     # Footnote formatting (footnote/endnote standardization)
│   ├── custom-format-manager/  # Custom format configuration management (WEB interface)
│   ├── margin-manager/         # Margin management (government/academic standards)
│   ├── preview-design/         # Design preview & user confirmation (Web interface)
│   ├── image-layout/           # Image layout optimization
│   ├── translation-engine/     # Chinese-English translation
│   ├── pdf-export/             # PDF export
│   └── report-generator/       # Report generation
├── workspace/                  # Workspace (created at runtime)
│   ├── input/                  # Input files
│   ├── output/                 # Output files
│   └── reports/                # Processing reports
├── requirements.txt            # Python dependencies
└── install_requirements.bat    # Dependency installation script
```

## Processing Flow

```text
Phase 0: Input Format Compatibility
    doc-compatibility (.doc → .docx)
    markdown-converter (.md/.txt → .docx, with math formula processing)

Phase 1: Parsing & Format Quality Detection
    docx-parser → Format quality detection (formatted / zero-format)

Phase 2: Formatted Path
    xml-safety → formula-protection → template-engine → font-manager
    → preview-design (user confirmation) → format-normalizer → table-processor → footnote-processor → margin-manager → image-layout

Phase 2b: Zero-format Path
    template-engine → font-manager → preview-design (user confirmation)
    → zero-format-normalizer → table-processor → footnote-processor → margin-manager → image-layout

Phase 3: Post-processing
    translation-engine (optional)
    pdf-export (optional)
    report-generator
```

### Input Format Support
The system supports multiple input formats, auto-detect and convert:
- **DOCX** - Direct processing
- **DOC** - Auto convert to .docx (using Word COM or LibreOffice)
- **Markdown (.md)** - Use pandoc to convert to .docx, support LaTeX math formulas
- **Plain text (.txt)** - Intelligently detect Markdown content and convert

### Format Quality Detection
The system automatically detects document format quality to decide processing path:
- **Formatted**: Document has heading styles, font configuration, paragraph formatting → Formatted path
- **Zero-format**: Document has no formatting, only plain text content → Zero-format path

### Table Formatting
After format standardization, automatically format tables according to academic paper standards:

| Item | Specification |
|------|---------------|
| Table position | Center aligned |
| Border style | Three-line table (top/bottom 1.5pt solid, header 0.75pt solid, no vertical lines) |
| Header font | Bold 10.5pt, center aligned |
| Body font | 10.5pt, center aligned |
| Line spacing | Single spacing |
| Cell margin | 0.1cm inner margin |
| Caption position | Above table |
| Caption font | Bold 10.5pt, center aligned |
| Caption format | "Table X-X Caption Content" |
| Caption & table | Keep on same page (keep with next) |
| Images in table | Preserve without compression |

### Footnote Formatting
After format standardization, automatically format footnotes and endnotes according to academic paper standards:

| Item | Specification |
|------|---------------|
| Footnote size | 9pt |
| Footnote font | Chinese: Song, English: Times New Roman |
| Footnote line spacing | Single spacing |
| Numbering format | Superscript Arabic numbers |
| Separator line | 0.5pt solid, 1/3 page width |
| Endnote position | End of document or section |

Configuration options (in template file `footnote` section):
| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | true | Enable footnote processing |
| `font_size` | 9 | Footnote size (pt) |
| `line_spacing` | single | Footnote line spacing |
| `numbering` | arabic | Numbering format: arabic/roman/symbol |
| `separator_length` | 25 | Separator line length (mm) |

## Template Description

Built-in templates are located in `SKILLS/format-normalizer/custom/`:

| Template File | Standard | Description |
|---------------|----------|-------------|
| `chinese_academic.yaml` | GB/T 7713.1-2006 | Chinese academic paper |
| `english_academic.yaml` | APA 7th Edition | English paper |

### Chinese Academic Paper Standard (GB/T 7713.1-2006)
- Page: A4, margins top 25.4mm bottom 25.4mm left 31.7mm right 25.4mm
- Body: Small 4 Song, 1.5x line spacing
- Heading 1: Size 4 Bold, center aligned
- Heading 2: Small 4 Bold, left aligned
- Heading 3: Small 4 Song, left aligned

### English Paper Standard (APA 7th Edition)
- Page: A4/Letter, margins 2.54cm (1 inch)
- Body: 12pt Times New Roman, double spacing
- Heading: 12pt Times New Roman, bold
- First line indent: 0.5 inch (1.27cm)

Support custom YAML/JSON templates.

## Notes

- System uses non-destructive processing, will not modify original files
- All operations can be rolled back
- Large documents (>200 pages) automatically enable chunked processing
- Table of contents uses Word TOC field code generation, open document and press `Ctrl+A` then `F9` to update fields and display page numbers
- Headers and footers are written through Word underlying XML, compatible with WPS and LibreOffice

## License

GPL 3.0
