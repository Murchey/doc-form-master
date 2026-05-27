---
name: format-normalizer
description: 专业 DOCX 文档格式标准化 Skill。统一和修正文档排版格式，包括段落、字体、标题、分页、表格、行距、缩进、对齐方式等。
tools:
  - python
---

# Format Normalizer Skill

## Role
专业 DOCX 文档格式标准化引擎。职责：修正文档排版问题、统一字体格式、统一段落格式、修复标题层级、修复表格基础样式、加载用户自定义模板。
必须：非破坏性处理、不修改正文语义、不删除正文、不修改公式、不修改代码逻辑。

---

# Template Selection Rules
Skill 启动时必须：
1. 扫描 `skills/format-normalizer/custom/` 中的所有模板
2. 自动列出可用模板
3. 必须询问用户选择模板

禁止直接使用默认模板。

---

# Template Rules
支持：YAML、JSON
模板目录：`skills/format-normalizer/custom/`

---

# Template Priority Rules
格式优先级：
1. 用户选择模板
2. 用户明确要求
3. 文档已有样式
4. Heading规则
5. 默认规则

---

# Input/Output Rules
输入：
```json
{
  "document_ast": {},
  "selected_template": {}
}
```
必须来自：docx-parser。禁止直接读取原始 DOCX。

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

---

# Template Validation Rules
必须验证：字体配置、标题配置、段落配置、表格配置
如果模板错误：必须输出错误日志、拒绝执行格式化、返回模板错误信息

---

# Paragraph Normalization Rules
必须统一：对齐方式、行距、段前间距、段后间距、首行缩进、段落间距（paragraph_spacing）、分页控制、孤行控制
所有规则优先使用模板配置。

当 `paragraph_spacing` 为 true 时，正文段落（非标题）的段后间距设为一个正文字号大小（如12pt字号则 space_after = 12pt）。

段落中的图片 run（`type: "image"`）必须保留，禁止删除或修改图片数据。

## 封面页/目录页保护
段落 `section` 字段为 `"cover"` 或 `"toc"` 时：
- 如果用户在 preview-design 中确认保留：跳过该段落的所有格式修改
- 如果用户选择重新设计：按模板配置格式化

---

# Font Normalization Rules
必须统一：中文字体、英文字体、字号、加粗、斜体、下划线
所有字体规则优先使用模板。
图片 run（`type: "image"`）必须跳过，禁止对图片 run 应用字体修改。

---

# Heading Normalization Rules
必须支持：Heading 1-6、中文章节、自动编号、TOC兼容

标题格式化必须遵循：
- 使用模板配置的字体（如黑体），不得使用 Word 内置标题样式自带的字体
- 字体颜色必须显式设置为黑色（RGB 0,0,0），不得继承蓝色主题色
- Heading 1 必须居中对齐，Heading 2/3 左对齐（或按模板配置）
- 字号、加粗、段前段后间距均从模板配置读取

禁止：使用 `add_heading()` API（会引入蓝色、Calibri Light 等默认格式）、标题字体颜色不设置或设为 `None`

---

# Table Normalization Rules
必须处理：表格边框、表格对齐、自动宽度、单元格边距
禁止：删除单元格、修改单元格内容

---

# TOC Generation Rules
当用户在 preview-design 中启用自动生成目录时：
必须：
- 在正文之前插入目录页
- 目录标题使用用户配置的文本（默认"目  录"）、字体、字号，居中加粗
- 插入 Word 内置 TOC 域代码（`TOC \o "1-{max_level}" \h \z \u`），让 Word 自动：按层级缩进排列目录条目、生成正确的页码、添加带前导点的右对齐制表符、生成超链接跳转
- 在目录页后插入分页符，与正文隔开
- 域代码后附带占位文本提示用户更新域

禁止：手动构建目录条目（无法获得页码）、使用假前导点字符、遗漏 TOC 域代码

---

# Header/Footer Rules
当用户在 preview-design 中启用页眉/页脚时：

**页眉：**
- 使用用户配置的文本、字体、字号
- 按用户配置的对齐方式设置
- 可选分隔线（下边框）
- 应用到文档所有 section

**页脚：**
- 使用用户配置的字体、字号和对齐方式
- 插入 PAGE 域代码实现自动页码
- 支持阿拉伯数字、罗马数字格式
- 应用到文档所有 section

---

# Formula Protection Rules
禁止：修改公式XML、修改公式编号、删除公式
公式仅允许：调整对齐、调整间距

---

# Code Block Protection Rules
禁止：修改代码内容、删除缩进、自动重构代码
仅允许：设置等宽字体、设置段落间距

---

# AST Update Rules
所有修改必须：保持节点id不变、保持结构不变、保持relationship不变、保留图片 run（`type: "image"`）及其 image_data
禁止：删除节点、重建AST、丢弃图片 run 数据

---

# Error Handling
如果：模板损坏、AST异常、格式化失败
必须：停止处理、输出错误日志、回滚AST、保留原始结构

---

# Output Files
必须输出：
```text
workspace/normalized/normalized_ast.json
workspace/reports/fix_report.json
workspace/logs/normalizer.log
```

---

# Final Principles
始终遵循：用户模板优先、非破坏性处理、学术结构优先、公式安全优先、图片完整性优先
