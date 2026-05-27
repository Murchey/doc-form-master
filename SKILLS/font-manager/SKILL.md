---
name: font-manager
description: 专业 DOCX 字体管理与字体兼容 Skill。检测系统字体、验证模板字体、自动 fallback、修复字体缺失问题。
tools:
  - python
---

# Font Manager Skill

## Role
专业 DOCX 字体兼容管理引擎。职责：检测系统字体、验证模板字体、自动 fallback、保证 PDF 导出字体安全、保证跨平台字体兼容。
必须：非破坏性处理、不删除字体、不覆盖系统字体、不修改原始模板。

---

# 为什么需要 Font Manager
DOCX 与 PDF 导出依赖系统字体。如果字体缺失，可能导致：PDF乱码、分页错乱、行距异常、图片错位、数学公式错位。
因此必须：自动检测字体、自动 fallback、自动警告用户。

---

# Supported Platforms
必须支持：Windows、Linux、macOS

---

# Supported Font Types
必须支持：中文字体、英文字体、等宽字体、数学公式字体、PDF嵌入字体

---

# Input/Output Rules
输入：
```json
{
  "template_config": {},
  "document_ast": {}
}
```
必须来自：template-engine

输出：
```json
{
  "available_fonts": [],
  "missing_fonts": [],
  "font_mapping": {},
  "fallback_mapping": {},
  "validation_report": {}
}
```

---

# Processing Pipeline
严格按照以下顺序执行：
1. Detect operating system
2. Scan system fonts
3. Load template fonts
4. Validate required fonts
5. Detect missing fonts
6. Apply fallback mapping
7. Validate PDF compatibility
8. Generate font report
9. Export validated mapping

---

# Font Detection Rules
必须检测：中文字体、英文字体、等宽字体、数学字体

---

# Supported Chinese Fonts
优先支持：宋体、黑体、仿宋_GB2312、楷体、微软雅黑

---

# Supported English Fonts
优先支持：Times New Roman、Arial、Calibri、Cambria

---

# Supported Code Fonts
优先支持：Consolas、Courier New、JetBrains Mono、Fira Code

---

# Fallback Rules
如果字体缺失，必须自动 fallback。

## 中文字体 Fallback
```yaml
宋体:
  - SimSun
  - Noto Serif CJK SC
  - Source Han Serif SC

黑体:
  - SimHei
  - Noto Sans CJK SC
  - Source Han Sans SC
```

## 英文字体 Fallback
```yaml
Times New Roman:
  - Liberation Serif
  - DejaVu Serif
```

## 等宽字体 Fallback
```yaml
Consolas:
  - Courier New
  - JetBrains Mono
  - Fira Code
```

---

# Font Validation Rules
必须验证：字体是否存在、字体是否可用于PDF、字体是否支持Unicode、字体是否支持中文

---

# PDF Font Rules
PDF导出前必须：检测字体存在、检测 fallback、检测中文支持、检测嵌入兼容

---

# Linux Compatibility Rules
Linux 默认缺少：宋体、黑体、仿宋、楷体
因此必须自动 fallback。推荐：Noto CJK、Source Han Serif、Source Han Sans

---

# Font Mapping Rules
所有字体最终必须映射为：
```json
{
  "宋体": "Noto Serif CJK SC",
  "黑体": "Noto Sans CJK SC"
}
```

---

# Security Rules
禁止：修改系统字体、删除字体、覆盖字体、自动安装商业字体
仅允许：检测、fallback、映射

---

# Error Handling
如果：字体缺失、fallback 失败、PDF 字体不兼容
必须：输出警告日志、自动 fallback、保留原配置、不中断流程

---

# Output Files
必须输出：
```text
workspace/validated/font_mapping.json
workspace/reports/font_report.json
workspace/logs/font_manager.log
```

---

# Final Principles
始终遵循：字体兼容性优先、PDF 稳定性优先、fallback 安全优先、非破坏性处理、跨平台兼容优先
