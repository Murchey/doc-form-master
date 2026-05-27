---
name: pdf-export
description: 专业 DOCX 转 PDF 导出 Skill。支持 Windows Word COM 和 LibreOffice 两种导出引擎。
tools:
  - python
---

# PDF Export Skill

## Role
专业 DOCX 转 PDF 导出引擎。职责：将格式化后的 DOCX 文件导出为高质量 PDF，保持排版稳定、图片清晰、公式完整。
必须：非破坏性处理、不修改 DOCX 源文件、不压缩图片、不丢失字体。

---

# Supported Export Engines
必须支持：
- **Windows**: Microsoft Word COM 接口（优先）
- **跨平台**: LibreOffice headless 模式

自动检测：优先使用 Word COM，不可用时 fallback 到 LibreOffice。

---

# Input/Output Rules
输入：
```json
{
  "docx_path": "",
  "font_mapping": {}
}
```
必须来自：format-normalizer。禁止直接读取原始 DOCX。

输出：
```json
{
  "pdf_path": "",
  "export_engine": "",
  "pdf_pages": 0,
  "export_success": true,
  "errors": []
}
```

---

# Processing Pipeline
严格按照以下顺序执行：
1. Load DOCX path
2. Detect export engine
3. Validate DOCX file
4. Export to PDF
5. Validate PDF output
6. Count pages
7. Generate export report
8. Return PDF path

---

# Word COM Export Rules
Windows 环境下必须：
- 使用 `win32com.client.Dispatch("Word.Application")`
- 设置 `word.Visible = False`
- 设置 `word.DisplayAlerts = False`
- 使用 `ExportAsFixedFormat` 方法
- 导出后关闭文档和 Word 应用

```python
doc.ExportAsFixedFormat(
    OutputFileName=pdf_path,
    ExportFormat=17,  # wdExportFormatPDF
    OpenAfterExport=False,
    OptimizeFor=0,    # wdExportOptimizeForPrint
    Range=0,          # wdExportAllDocument
    IncludeDocProps=True,
    KeepIRM=True,
    CreateBookmarks=0,
    DocStructureTags=True,
    BitmapMissingFonts=False,
    UseISO19005_1=False
)
```

---

# LibreOffice Export Rules
非 Windows 环境下必须：
```bash
libreoffice --headless --convert-to pdf:writer_pdf_Export input.docx --outdir output_dir
```

---

# PDF Validation Rules
必须验证：PDF 文件存在、PDF 可读取、页数大于 0

---

# Error Handling
如果：DOCX 文件不存在、导出引擎不可用、PDF 导出失败、PDF 文件损坏
必须：输出错误日志、保留原始 DOCX、不输出损坏 PDF

---

# Output Files
必须输出：
```text
workspace/exported/final.pdf
workspace/reports/pdf_export_report.json
workspace/logs/pdf_export.log
```

---

# Final Principles
始终遵循：PDF 质量优先、字体嵌入安全、图片清晰度优先、非破坏性导出、跨平台兼容
