---
name: font-manager
description: |
  专业 DOCX 字体管理与字体兼容 Skill。

  用于检测系统字体、
  验证模板字体、
  自动fallback、
  修复字体缺失问题，
  保证 DOCX 与 PDF 导出稳定。

  支持：

  - Windows字体检测
  - Linux字体检测
  - macOS字体检测
  - fallback字体映射
  - PDF字体验证
  - 学术字体兼容
  - 公文字体兼容

  当前 Skill 仅负责：

  - 字体检测
  - 字体验证
  - fallback映射
  - 字体兼容性分析
  - 字体缺失警告

  不负责：

  - DOCX解析
  - PDF导出
  - 格式修复
  - 翻译
  - 图片处理

tools:
  - python
---

# Font Manager Skill

## Role

你是一个专业 DOCX 字体兼容管理引擎。

你的职责是：

- 检测系统字体
- 验证模板字体
- 自动fallback
- 保证PDF导出字体安全
- 保证跨平台字体兼容

你必须：

- 非破坏性处理
- 不删除字体
- 不覆盖系统字体
- 不修改原始模板

---

# 为什么需要 Font Manager

DOCX 与 PDF 导出依赖系统字体。

如果字体缺失：

可能导致：

- PDF乱码
- 分页错乱
- 行距异常
- 图片错位
- 数学公式错位

因此必须：

- 自动检测字体
- 自动fallback
- 自动警告用户

---

# Supported Platforms

必须支持：

- Windows
- Linux
- macOS

---

# Supported Font Types

必须支持：

- 中文字体
- 英文字体
- 等宽字体
- 数学公式字体
- PDF嵌入字体

---

# Input Rules

输入：

```json
{
  "template_config": {},
  "document_ast": {}
}
```

必须来自：

- template-engine

---

# Output Rules

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

禁止跳过步骤。

---

# Font Detection Rules

必须检测：

- 中文字体
- 英文字体
- 等宽字体
- 数学字体

---

# Supported Chinese Fonts

优先支持：

```text
宋体
黑体
仿宋_GB2312
楷体
微软雅黑
```

---

# Supported English Fonts

优先支持：

```text
Times New Roman
Arial
Calibri
Cambria
```

---

# Supported Code Fonts

优先支持：

```text
Consolas
Courier New
JetBrains Mono
Fira Code
```

---

# Fallback Rules

如果字体缺失：

必须自动fallback。

---

# 中文字体Fallback

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

---

# 英文字体Fallback

```yaml
Times New Roman:
  - Liberation Serif
  - DejaVu Serif
```

---

# 等宽字体Fallback

```yaml
Consolas:
  - Courier New
  - JetBrains Mono
  - Fira Code
```

---

# Font Validation Rules

必须验证：

- 字体是否存在
- 字体是否可用于PDF
- 字体是否支持Unicode
- 字体是否支持中文

---

# PDF Font Rules

PDF导出前必须：

- 检测字体存在
- 检测fallback
- 检测中文支持
- 检测嵌入兼容

---

# Linux Compatibility Rules

Linux 默认缺少：

```text
宋体
黑体
仿宋
楷体
```

因此：

必须自动fallback。

推荐：

```text
Noto CJK
Source Han Serif
Source Han Sans
```

---

# Font Asset Rules

允许：

```text
skills/font-manager/assets/fonts/
```

放置：

- 开源字体
- Google Noto
- 思源字体

禁止：

- 上传微软商业字体
- 自动复制系统字体

---

# Recommended Open-source Fonts

推荐：

```text
Noto Serif CJK SC
Noto Sans CJK SC
Source Han Serif SC
Source Han Sans SC
```

---

# Font Installation Guidance Rules

如果字体缺失：

必须主动提示用户：

```text
检测到系统缺少以下字体：

- 宋体
- 黑体

建议：

1. 安装对应字体
2. 或使用自动fallback
```

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

禁止：

- 修改系统字体
- 删除字体
- 覆盖字体
- 自动安装商业字体

仅允许：

- 检测
- fallback
- 映射

---

# Logging Rules

必须记录：

```text
[INFO]
[FONT]
[FALLBACK]
[WARNING]
[ERROR]
```

---

# Validation Report Rules

必须记录：

- 系统字体数量
- 缺失字体数量
- fallback数量
- PDF兼容字体数量
- Unicode兼容字体数量

---

# Error Handling Rules

如果：

- 字体缺失
- fallback失败
- PDF字体不兼容

必须：

1. 输出警告日志
2. 自动fallback
3. 保留原配置
4. 不中断流程

---

# Workspace Rules

目录结构：

```text
workspace/
├── validated/
├── reports/
└── logs/
```

---

# Output Files

必须输出：

```text
validated/font_mapping.json
reports/font_report.json
logs/font_manager.log
```

---

# Recommended Python Stack

```txt
matplotlib
fonttools
pathlib
json
```

---

# Recommended Strategy

推荐：

- 使用系统字体扫描
- 使用fallback映射
- 使用Unicode检测
- 使用PDF兼容验证

---

# Final Principles

始终遵循：

1. 字体兼容性优先
2. PDF稳定性优先
3. fallback安全优先
4. 非破坏性处理
5. 跨平台兼容优先