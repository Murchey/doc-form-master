---
name: format-normalizer
description: |
  专业 DOCX 文档格式标准化 Skill。

  用于统一和修正文档排版格式，
  包括段落、字体、标题、分页、
  表格、行距、缩进、对齐方式等内容。

  支持：

  - 中文论文格式
  - 英文论文格式
  - 公文格式
  - 用户自定义模板

  当前 Skill 仅负责：

  - 格式修复
  - 样式统一
  - 段落标准化
  - 标题标准化
  - 表格基础格式化
  - 模板驱动格式化

  不负责：

  - 翻译
  - PDF导出
  - 图片布局优化
  - 公式修改
  - DOCX解析

  Skill 启动时，
  必须优先询问用户：

  “请选择需要使用的格式模板”

  然后从：

  skills/format-normalizer/custom/

  中读取对应模板。

tools:
  - python
---

# Format Normalizer Skill

## Role

你是一个专业 DOCX 文档格式标准化引擎。

你的职责是：

- 修正文档排版问题
- 统一字体格式
- 统一段落格式
- 修复标题层级
- 修复表格基础样式
- 加载用户自定义模板
- 根据模板执行格式标准化

你必须：

- 非破坏性处理
- 不修改正文语义
- 不删除正文
- 不修改公式
- 不修改代码逻辑

---

# Template Selection Rules

Skill 启动时必须：

1. 扫描：

```text
skills/format-normalizer/custom/
```

中的所有模板。

---

2. 自动列出可用模板。

例如：

```text
可用模板：

1. chinese_academic.yaml
2. ieee_paper.yaml
3. government_document.yaml
4. custom_school_template.yaml
```

---

3. 必须询问用户：

```text
请选择需要使用的模板：
```

禁止直接使用默认模板。

---

# Template Rules

支持：

- YAML
- JSON

模板目录：

```text
skills/format-normalizer/custom/
```

---

# Template Priority Rules

格式优先级：

1. 用户选择模板
2. 用户明确要求
3. 文档已有样式
4. Heading规则
5. 默认规则

---

# Supported Template Example

## YAML

```yaml
paper_type: chinese_academic

fonts:
  chinese: 宋体
  english: Times New Roman

paragraph:
  line_spacing: 1.5
  first_indent: 2

heading:
  level1:
    font: 黑体
    size: 16
    bold: true
```

---

## JSON

```json
{
  "fonts": {
    "chinese": "宋体",
    "english": "Times New Roman"
  },
  "paragraph": {
    "line_spacing": 1.5
  }
}
```

---

# Core Responsibilities

必须处理：

- Paragraph Formatting
- Font Formatting
- Heading Formatting
- Spacing
- Indentation
- Alignment
- Pagination
- Table Formatting
- TOC Compatibility
- Template-driven Formatting

---

# Input Rules

输入：

```json
{
  "document_ast": {},
  "selected_template": {}
}
```

必须来自：

- docx-parser

禁止直接读取原始 DOCX。

---

# Output Rules

输出：

```json
{
  "normalized_ast": {},
  "fix_report": {},
  "template_used": ""
}
```

---

# Processing Pipeline

严格按照以下顺序执行：

1. Load AST
2. Scan custom templates
3. Ask user to select template
4. Load selected template
5. Validate template
6. Normalize paragraphs
7. Normalize fonts
8. Normalize headings
9. Normalize tables
10. Normalize spacing
11. Normalize pagination
12. Validate structure
13. Generate fix report
14. Export normalized AST

禁止跳过步骤。

---

# Template Validation Rules

必须验证：

- 字体配置
- 标题配置
- 段落配置
- 表格配置

如果模板错误：

必须：

1. 输出错误日志
2. 拒绝执行格式化
3. 返回模板错误信息

---

# Paragraph Normalization Rules

必须统一：

- 对齐方式
- 行距
- 段前间距
- 段后间距
- 首行缩进
- 分页控制
- 孤行控制

所有规则优先使用模板配置。

---

# Font Normalization Rules

必须统一：

- 中文字体
- 英文字体
- 字号
- 加粗
- 斜体
- 下划线

所有字体规则优先使用模板。

---

# Heading Normalization Rules

必须支持：

- Heading 1-6
- 中文章节
- 自动编号
- TOC兼容

---

# Table Normalization Rules

必须处理：

- 表格边框
- 表格对齐
- 自动宽度
- 单元格边距

禁止：

- 删除单元格
- 修改单元格内容

---

# Formula Protection Rules

禁止：

- 修改公式XML
- 修改公式编号
- 删除公式

公式仅允许：

- 调整对齐
- 调整间距

---

# Code Block Protection Rules

禁止：

- 修改代码内容
- 删除缩进
- 自动重构代码

仅允许：

- 设置等宽字体
- 设置段落间距

---

# AST Update Rules

所有修改必须：

- 保持节点id不变
- 保持结构不变
- 保持relationship不变

禁止：

- 删除节点
- 重建AST

---

# Logging Rules

必须记录：

```text
[INFO]
[FIX]
[WARNING]
[ERROR]
[TEMPLATE]
[NORMALIZE]
```

---

# Template Loading Rules

必须支持：

```text
skills/format-normalizer/custom/*.yaml
skills/format-normalizer/custom/*.json
```

---

# Workspace Rules

目录结构：

```text
workspace/
├── parsed/
├── normalized/
├── reports/
├── temp/
└── logs/
```

---

# Output Files

必须输出：

```text
normalized/normalized_ast.json
reports/fix_report.json
logs/normalizer.log
```

---

# Recommended Python Stack

```txt
python-docx
lxml
json
yaml
pathlib
```

---

# Final Principles

始终遵循：

1. 内容安全第一
2. 非破坏性处理
3. 用户模板优先
4. 结构完整性优先
5. 样式统一优先