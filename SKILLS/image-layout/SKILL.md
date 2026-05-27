---
name: image-layout
description: 专业 DOCX 图片布局优化 Skill。检测、分析、保护和优化文档中的图片布局，保持图文关系稳定。
tools:
  - python
---

# Image Layout Skill

## Role
专业 DOCX 图片布局优化引擎。职责：检测文档图片、分析图片布局、修复图片位置、保持图文关系、防止图片跨页、防止图片覆盖正文、保持图片清晰度、优化学术论文图片布局。
必须：非破坏性处理、不修改图片内容、不降低图片质量、不删除图片、不破坏 relationship。

---

# Supported Image Types
必须支持：Inline Image、Floating Image、Embedded Image、Linked Image、Figure Caption、Academic Figures

---

# Input/Output Rules
输入：
```json
{
  "document_ast": {},
  "image_nodes": []
}
```
必须来自：docx-parser。禁止直接修改原始 DOCX。

输出：
```json
{
  "optimized_images": [],
  "layout_report": {},
  "validated_ast": {}
}
```

---

# Processing Pipeline
严格按照以下顺序执行：
1. Load AST
2. Detect image nodes
3. Detect caption relationship
4. Analyze image position
5. Analyze page overflow
6. Analyze floating conflicts
7. Optimize image layout
8. Validate relationship safety
9. Generate layout report
10. Export optimized AST

---

# Image Detection Rules
必须检测：Inline images、Floating images、DrawingML、Embedded media、Figure captions、Anchor positions

---

# Image Layout Rules
必须：图片默认居中、保持图片宽高比、不超出页边距、图片与标题保持关联、图片与正文保持合理间距

默认规则：
```yaml
alignment: center
keep_ratio: true
max_width_percent: 80
spacing_before: 12
spacing_after: 12
```

---

# Academic Figure Rules
学术论文图片必须：紧跟引用段落、图题位于图片下方、图片居中、保持编号关系、避免跨页断裂

---

# Caption Binding Rules
必须保护：Figure Caption、图片编号、图文引用关系
禁止：图片与Caption分离、Caption跨页、Caption编号丢失

---

# Cross-page Protection Rules
必须防止：图片跨页、图片断裂、Caption单独分页
优先策略：图片整体移动、保持图文绑定、保持分页完整

---

# Floating Image Rules
必须检测：floating overlap、text overlap、page overflow
禁止：图片覆盖正文、图片超出页面、图片遮挡页码

---

# Image Scaling Rules
如果图片过大：必须等比缩放、保持清晰度、保持居中
禁止：拉伸图片、压缩失真、改变宽高比

---

# Relationship Protection Rules
必须保护：image relationship id、media path、drawing relationship
禁止：删除relationship、修改image reference、修改media路径

---

# XML Safety Rules
必须保护：`<a:blip>`、`<pic:pic>`、`<w:drawing>`
禁止：删除drawing XML、修改anchor XML、删除inline节点

---

# Image Translation Protection
禁止：翻译图片内容、OCR替换图片、修改图片文字
仅允许：调整位置、调整布局

---

# AST Protection Rules
所有图片节点必须：保持id不变、保持relationship不变、保持media路径不变
禁止：删除图片节点、重建图片节点

---

# Error Handling
如果：relationship丢失、图片缺失、media路径错误、drawing XML异常
必须：停止处理、输出错误日志、回滚AST、保留原始结构

---

# Output Files
必须输出：
```text
workspace/optimized/image_layout_ast.json
workspace/reports/image_layout_report.json
workspace/logs/image_layout.log
```

---

# Final Principles
始终遵循：图片完整性第一、relationship安全优先、图文关系优先、非破坏性处理、学术布局优先
