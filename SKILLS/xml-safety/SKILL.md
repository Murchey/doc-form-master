---
name: xml-safety
description: 专业 DOCX XML 安全保护 Skill。保护 styles、relationships、namespace、numbering、section 等关键结构。
tools:
  - python
---

# XML Safety Skill

## Role
专业 DOCX XML 安全保护引擎。职责：验证 DOCX XML 完整性、保护 namespace、relationship、styles.xml、numbering.xml、section properties。
必须：非破坏性处理、不修改正文内容、不删除XML节点、不修改relationship id、不修改namespace。

---

# Supported XML Types
必须支持：document.xml、styles.xml、numbering.xml、settings.xml、footnotes.xml、endnotes.xml、document.xml.rels

---

# Input/Output Rules
输入：
```json
{
  "docx_path": "",
  "document_ast": {}
}
```
必须来自：docx-parser。禁止直接覆盖原DOCX。

输出：
```json
{
  "xml_validation": {},
  "relationship_report": {},
  "namespace_report": {},
  "safe_ast": {}
}
```

---

# Processing Pipeline
严格按照以下顺序执行：
1. Validate DOCX ZIP
2. Extract XML files
3. Validate XML encoding
4. Validate namespace
5. Validate relationship
6. Validate styles.xml
7. Validate numbering.xml
8. Validate section properties
9. Validate formula namespace
10. Detect orphan relationships
11. Generate safety report
12. Export validated AST

---

# Protection Rules

## Namespace Protection
必须保护：xmlns:w=、xmlns:r=、xmlns:m=、xmlns:a=、xmlns:pic=
禁止：namespace删除、重命名、覆盖、污染

## Relationship Protection
必须保护：image relationship、style relationship、numbering relationship、header/footer relationship、footnote relationship
禁止：relationship id修改、丢失、重复、orphan relationship

## styles.xml Rules
必须保护：style id、heading style、paragraph style、character style、table style
禁止：删除style、修改style id、删除默认style

## numbering.xml Rules
必须保护：abstractNum、numId、heading numbering、list numbering
禁止：numbering id修改、numbering丢失、heading numbering断裂

## Section Protection
必须保护：page size、page margin、columns、header/footer reference
禁止：删除section、修改section relationship、section断裂

## Formula XML Rules
必须保护：`<m:oMath>`、`<m:oMathPara>`
禁止：删除math namespace、修改math XML、删除公式节点

---

# Validation Rules
必须检测：malformed XML、missing namespace、invalid relationship、duplicated id、orphan node
禁止：自动修复XML、自动删除节点、自动重建relationship。仅允许：检测、验证、报告。

---

# Error Handling
如果：XML损坏、namespace丢失、relationship异常、ZIP结构损坏
必须：停止后续处理、输出错误日志、保留原始DOCX、阻止导出

---

# Output Files
必须输出：
```text
workspace/validated/xml_safe_ast.json
workspace/reports/xml_safety_report.json
workspace/logs/xml_safety.log
```

---

# Final Principles
始终遵循：XML安全第一、namespace安全优先、relationship安全优先、非破坏性验证、DOCX结构完整性优先
