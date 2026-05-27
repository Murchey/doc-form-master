---
name: zero-format-normalizer
description: 零格式DOCX格式化Skill。从完全没有格式的DOCX文件开始，应用模板配置生成规范格式的文档。
tools:
  - python
---

# Zero Format Normalizer Skill

## Role
零格式DOCX格式化引擎。职责：从完全没有格式的DOCX文件中提取文本内容，按照模板配置生成规范格式的文档。
必须：保留所有文本内容、保留图片、保留表格结构、应用模板配置的格式。

---

# Input/Output Rules
输入：
```json
{
  "source_docx": "path/to/zero_format.docx",
  "template_config": {}
}
```

输出：
```json
{
  "formatted_docx": "path/to/formatted.docx",
  "report": {}
}
```

---

# Processing Pipeline
严格按照以下顺序执行：
1. Load source DOCX
2. Extract text content (strip all formatting)
3. Parse document structure (headings, paragraphs, images, tables)
4. Apply template formatting
5. Generate TOC (if enabled)
6. Create sections (cover, toc, body, references)
7. Add header/footer
8. Save formatted DOCX

---

# Zero Format Processing Rules

## Text Extraction
- 提取所有文本内容，忽略原始格式
- 保留段落边界（每个段落独立处理）
- 保留图片（从原始DOCX中提取）
- 保留表格结构（行、列、内容）

## Structure Detection
自动检测文档结构：
- **封面页**：检测前几段是否包含标题、作者、日期等信息
- **目录页**：检测是否包含"目录"、"Table of Contents"等关键词
- **标题**：检测编号模式（如"1."、"2.1"、"3.1.2"）或特殊格式
- **正文**：普通段落
- **参考文献**：检测"参考文献"、"References"等关键词

## Formatting Rules
- 所有文本使用模板配置的字体
- 所有段落使用模板配置的对齐方式
- 标题使用模板配置的标题样式
- 图片居中对齐
- 表格使用模板配置的表格样式

---

# Template Configuration
支持以下配置项：

```yaml
fonts:
  chinese:
    family: 宋体
    size: 12
  english:
    family: Times New Roman
    size: 12

heading:
  level1:
    font: 黑体
    size: 14
    bold: true
    alignment: center
  level2:
    font: 黑体
    size: 12
    bold: true
    alignment: left

paragraph:
  alignment: justify
  line_spacing: 1.5
  first_indent: 2

toc:
  enabled: true
  max_level: 3

header:
  enabled: true
  text: "文档标题"

footer:
  enabled: true
  page_number: true
```

---

# Image Processing Rules
- 从原始DOCX中提取所有图片
- 保留图片格式（JPEG、PNG、GIF等）
- 应用模板配置的图片样式（居中、最大宽度等）
- 保留图片与文本的关联关系

---

# Table Processing Rules
- 保留表格结构（行、列）
- 提取单元格文本内容
- 应用模板配置的表格样式
- 保留表格边框

---

# Section Management Rules
自动创建以下节结构：

| 节 | 内容 | 页眉 | 页脚 |
|---|---|---|---|
| 第1节 | 封面页 | 无 | 无 |
| 第2节 | 目录页 | 无 | 无 |
| 第3节 | 正文页 | 有（用户配置） | 有（页码从1开始） |
| 第4节 | 引用页 | 有（用户配置） | 无页码 |

---

# Non-Destructive Rules
- 不修改原始DOCX文件
- 创建新的DOCX文件作为输出
- 保留所有文本内容
- 保留所有图片
- 保留所有表格数据

---

# Error Handling
- 如果源DOCX文件不存在：抛出FileNotFoundError
- 如果源DOCX文件损坏：尝试修复或跳过损坏部分
- 如果图片提取失败：记录警告，继续处理其他内容
- 如果模板配置无效：使用默认配置

---

# Usage Example

```python
from zero_format_normalizer import ZeroFormatNormalizer

normalizer = ZeroFormatNormalizer(
    source_docx_path="input/zero_format.docx",
    template_config_path="template.yaml"
)
normalizer.run("output/formatted.docx")
```

---

# Limitations
- 不支持复杂的文档布局（如多栏、文本框）
- 不支持OLE对象（如嵌入的Excel表格）
- 不支持复杂的图表（如SmartArt）
- 不支持宏和VBA代码

---

# Future Enhancements
- 支持纯文本文件输入（.txt）
- 支持Markdown文件输入（.md）
- 支持HTML文件输入（.html）
- 智能段落合并（处理断行问题）
- 智能标题检测（基于字体大小、加粗等）
