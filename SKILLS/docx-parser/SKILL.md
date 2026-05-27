---
name: docx-parser
description: 专业 DOCX 文档结构解析 Skill。解析段落、Run、样式、表格、图片、公式、relationship、section 等，构建统一 Document AST。
tools:
  - python
---

# DOCX Parser Skill

## Role
专业 DOCX 结构解析引擎。职责：解析 DOCX 文件结构、提取文档核心元素、构建统一 AST、保持 XML 完整性。
必须：非破坏性解析、不修改原始文档、不修正格式、不翻译内容。

---

# Core Responsibilities
必须解析：Paragraph、Run、Style、Heading、Table、Image、Formula、Header/Footer、Footnote、Endnote、TOC、Section、Relationship、Numbering

---

# Input/Output Rules
输入：`.docx` 文件（支持 Microsoft Word、WPS、LibreOffice 导出的 DOCX）
禁止：doc、pdf、txt

输出统一 AST：
```json
{
  "metadata": {},
  "paragraphs": [],
  "tables": [],
  "images": [],
  "formulas": [],
  "styles": [],
  "sections": [],
  "section_regions": {}
}
```

---

# Processing Pipeline
严格按照以下顺序执行：
1. Validate DOCX
2. Create workspace copy
3. Extract ZIP structure
4. Parse XML files
5. Parse styles
6. Parse numbering
7. Parse paragraphs
8. Parse runs
9. Parse tables
10. Parse images
11. Parse formulas
12. Parse sections
13. Build AST
14. Validate AST
15. Export JSON

---

# DOCX Compatibility Rules
必须兼容：Office 2010+、WPS、LibreOffice、macOS Word
必须保留：styles.xml、numbering.xml、document.xml.rels、section properties

---

# XML Safety Rules
禁止：修改 namespace、修改 relationship id、删除 style 引用、删除 numbering 引用、修改 document.xml
当前 Skill 仅允许读取，不允许写入。

---

# Parsing Rules

## Paragraph Parsing
必须提取：paragraph id、text、style、alignment、spacing、indentation、page break、heading level

## Run Parsing
必须提取：text、bold、italic、underline、font、font size、color

## Table Parsing
必须提取：rows、cols、cell text、merged cells、borders、alignment

## Image Parsing
必须提取：image id、image path、image size、anchor position、inline/floating、relationship id

图片同时通过两种方式嵌入 AST：
1. **顶层 images 数组**：记录图片元数据（id、path）
2. **段落 runs 内联**：在对应段落的 runs 数组中插入 `{"type": "image"}` 条目

内联 image run 结构：
```json
{
  "type": "image",
  "image_data": "<base64 encoded binary>",
  "image_format": "png"
}
```

禁止：修改图片、压缩图片、丢弃图片数据

---

# Formula Parsing
必须支持：OMML、MathType、LaTeX converted equations
必须提取：formula xml、formula text、equation number
禁止：修改公式、删除 namespace

---

# AST Rules
统一输出结构：
```json
{
  "type": "paragraph",
  "text": "example",
  "style": "Heading1",
  "section": "body",
  "runs": []
}
```

runs 数组支持两种条目类型：
1. **文字 run** — 标准文本 run，包含 text / bold / italic / font_name / font_size 等字段
2. **图片 run** — 内联图片条目，结构如下：
```json
{
  "type": "image",
  "image_data": "<base64 encoded binary>",
  "image_format": "png"
}
```

图片 run 与文字 run 在 runs 数组中保持文档原始顺序。

---

# Section Identification
解析完成后，必须识别文档结构区域并为每个段落标记 `section` 字段：

| section 值 | 含义 | 检测规则 |
|---|---|---|
| `"cover"` | 封面页 | 文档开头到第一个实质内容 Heading 之间的段落（空段落 + 居中标题） |
| `"toc"` | 目录页 | 包含"目录"/"目 录"/"Table of Contents"文本的段落，或样式名含"TOC"的段落 |
| `"body"` | 正文 | 其余所有段落 |

AST 顶层必须包含 `section_regions` 字段：
```json
{
  "section_regions": {
    "cover_end": 5,
    "toc_start": 6,
    "toc_end": 15
  }
}
```

所有节点必须：type明确、id唯一、position可追踪、section已标记

---

# Error Handling Rules
如果：DOCX损坏、XML异常、relationship丢失
必须：输出错误日志、保留原文件、中止解析、不输出损坏AST

---

# Output Files
必须输出：
```text
workspace/parsed/document_ast.json
workspace/logs/parser.log
```

---

# Recommended Python Stack
```txt
python-docx
lxml
zipfile
pathlib
Pillow
xml.etree.ElementTree
```

---

# Final Principles
始终遵循：非破坏性解析、XML安全优先、内容完整性优先、Relationship安全优先、AST结构统一
