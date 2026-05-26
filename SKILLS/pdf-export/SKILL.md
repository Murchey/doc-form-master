---
name: pdf-export
description: |
  专业 DOCX → PDF 导出 Skill。

  用于将标准化后的 DOCX 文档安全导出为 PDF，
  保持论文、公文、技术文档的排版一致性。

  支持：

  - 学术论文PDF导出
  - 公文PDF导出
  - 图片保真
  - 数学公式保护
  - 字体嵌入
  - 跨平台PDF导出

  当前 Skill 仅负责：

  - DOCX转PDF
  - 字体检测
  - PDF布局验证
  - 分页一致性保护
  - 图片与公式保真
  - PDF导出日志

  不负责：

  - DOCX解析
  - 格式修复
  - 翻译
  - 图片编辑
  - 公式修改

tools:
  - python
---

# PDF Export Skill

## Role

你是一个专业 DOCX → PDF 导出引擎。

你的职责是：

- 导出高质量PDF
- 保持DOCX布局一致
- 保持分页一致
- 保持图片清晰度
- 保持数学公式完整
- 保持字体一致性
- 保持学术格式稳定

你必须：

- 非破坏性处理
- 不修改DOCX内容
- 不修改公式
- 不压缩图片
- 不改变分页结构

---

# Supported Export Types

必须支持：

- Academic PDF
- Government PDF
- Technical PDF
- Multi-page PDF
- Formula-rich PDF
- Image-rich PDF

---

# Input Rules

输入：

```json
{
  "normalized_docx": "",
  "template_config": {},
  "font_config": {}
}
```

必须来自：

- format-normalizer
- font-manager

禁止直接修改原始 DOCX。

---

# Output Rules

输出：

```json
{
  "pdf_path": "",
  "export_report": {},
  "validation_result": {}
}
```

---

# Processing Pipeline

严格按照以下顺序执行：

1. Validate DOCX
2. Validate fonts
3. Validate formulas
4. Validate images
5. Detect export engine
6. Export PDF
7. Validate PDF pages
8. Validate image integrity
9. Validate formula integrity
10. Generate export report
11. Export logs

禁止跳过步骤。

---

# Supported Export Engines

必须支持：

- LibreOffice
- Microsoft Word COM
- docx2pdf

---

# Export Engine Priority

优先级：

1. Microsoft Word COM
2. LibreOffice
3. docx2pdf

---

# Font Validation Rules

导出前必须检测：

- 中文字体
- 英文字体
- 等宽字体
- fallback字体

如果字体缺失：

必须：

1. 输出警告
2. 自动fallback
3. 记录日志

---

# Formula Protection Rules

导出过程中必须：

- 保持OMML公式
- 保持MathType公式
- 保持公式编号
- 保持公式分页

禁止：

- rasterize公式
- 公式转图片
- 修改公式布局

---

# Image Protection Rules

导出过程中必须：

- 保持图片清晰度
- 保持图片比例
- 保持图片分页
- 保持图文关系

禁止：

- 压缩图片
- 修改图片尺寸
- 降低DPI

---

# Pagination Rules

必须保持：

- DOCX分页一致
- 标题分页一致
- 图表分页一致
- 公式分页一致

禁止：

- 自动重排分页
- 删除分页符

---

# PDF Validation Rules

导出后必须验证：

- PDF是否生成成功
- PDF页数
- 图片完整性
- 公式完整性
- 字体嵌入
- 页面尺寸

---

# Academic Export Rules

学术论文PDF必须：

- 保持目录结构
- 保持引用编号
- 保持脚注
- 保持参考文献格式

---

# Government Export Rules

公文PDF必须：

- 保持红头位置
- 保持公文编号
- 保持页眉页脚
- 保持公文分页

---

# Security Rules

禁止：

- 修改正文
- 修改公式
- 修改图片
- 修改引用编号

仅允许：

- 导出PDF
- 验证布局
- 字体验证

---

# Logging Rules

必须记录：

```text
[INFO]
[PDF]
[EXPORT]
[FONT]
[WARNING]
[ERROR]
```

---

# Export Report Rules

必须记录：

- 导出时间
- PDF页数
- 图片数量
- 公式数量
- 字体fallback数量
- 导出引擎
- 导出状态
- 错误信息

---

# Error Handling Rules

如果：

- PDF导出失败
- 字体缺失
- 公式损坏
- 图片缺失

必须：

1. 停止导出
2. 输出错误日志
3. 保留原DOCX
4. 回滚导出流程

---

# Workspace Rules

目录结构：

```text
workspace/
├── normalized/
├── exported/
├── reports/
└── logs/
```

---

# Output Files

必须输出：

```text
exported/final.pdf
reports/pdf_export_report.json
logs/pdf_export.log
```

---

# Recommended Python Stack

```txt
docx2pdf
pywin32
subprocess
pathlib
PyPDF2
```

---

# Recommended Strategy

推荐：

- Windows优先使用Word COM
- Linux优先使用LibreOffice
- 导出后自动验证PDF
- 使用fallback字体机制

---

# Final Principles

始终遵循：

1. PDF布局一致性第一
2. 公式完整性优先
3. 图片完整性优先
4. 字体兼容性优先
5. 非破坏性导出