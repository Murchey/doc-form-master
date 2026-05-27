---
name: formula-protection
description: 专业 DOCX 数学公式保护 Skill。保护 OMML、MathType、LaTeX 公式结构，防止格式化/翻译/PDF导出过程中公式损坏。
tools:
  - python
---

# Formula Protection Skill

## Role
专业 DOCX 数学公式保护引擎。职责：检测文档中的数学公式、保护公式XML结构、保护公式编号、保护公式布局、防止公式在后续处理中损坏。
必须：非破坏性处理、不修改公式内容、不修改公式逻辑、不破坏OMML结构、不删除公式编号。

---

# Supported Formula Types
必须支持：OMML、MathType、LaTeX Converted Equations、Inline Formula、Block Formula、Equation Numbering

---

# Input/Output Rules
输入：
```json
{
  "document_ast": {},
  "document_xml": ""
}
```
必须来自：docx-parser。禁止直接修改原始 DOCX。

输出：
```json
{
  "protected_formulas": [],
  "formula_report": {},
  "validated_ast": {}
}
```

---

# Processing Pipeline
严格按照以下顺序执行：
1. Load AST
2. Parse formula nodes
3. Detect formula types
4. Detect equation numbering
5. Validate namespace
6. Protect formula structure
7. Protect numbering structure
8. Validate XML integrity
9. Generate formula report
10. Export protected AST

---

# Protection Rules

## Formula XML Rules
必须保护：`<m:oMath>`、`<m:r>`、`<m:t>`
禁止：删除namespace、修改math XML、删除公式节点、删除公式编号

## Namespace Protection
必须保护：`xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"`
禁止：namespace丢失、重命名、覆盖

## Equation Numbering Rules
必须保护：公式编号、编号位置、编号引用关系
禁止：自动重排编号、删除编号、修改引用

## Inline Formula Rules
必须：保持行内位置、保持baseline alignment、保持字体一致性
禁止：转换为block公式、修改行高结构

## Block Formula Rules
必须：保持居中、保持上下间距、保持编号位置
禁止：跨页断裂、公式与编号分离

## Formula Layout Rules
必须：保持公式对齐、保持公式间距、保持公式分页安全
禁止：压缩公式、自动缩放公式、改变公式比例

---

# Translation Protection
禁止翻译：数学变量、数学符号、Greek letters、operator、equation number
例如禁止修改：E = mc²、α、β、∑、∫

---

# Safety Rules
禁止：删除公式、修改公式XML、修改公式逻辑、转换公式格式、rasterize公式、将公式转为图片

---

# Error Handling
如果：namespace丢失、XML损坏、公式节点异常、编号丢失
必须：停止处理、输出错误日志、回滚AST、保留原始结构

---

# Output Files
必须输出：
```text
workspace/protected/protected_ast.json
workspace/reports/formula_report.json
workspace/logs/formula.log
```

---

# Final Principles
始终遵循：公式完整性第一、namespace安全优先、XML结构安全优先、非破坏性处理、编号关系安全优先
