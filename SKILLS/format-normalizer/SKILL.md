---
name: format-normalizer
description: 已格式化文档的格式标准化。
tools: [python]
---

# Format Normalizer

对已有格式的文档执行格式标准化。

**输入**：`protected_ast` + `template_config` + `font_mapping` + 源 DOCX 路径
**输出**：`workspace/output/formatted.docx`

---

# 调用方式

## AST 标准化（normalizer.py）

```python
import sys
sys.path.insert(0, 'SKILLS/format-normalizer/scripts')
from normalizer import FormatNormalizer

normalizer = FormatNormalizer(
    'workspace/parsed/document_ast.json',
    'workspace/validated/template_config.json'
)
normalizer.run()
# 输出: workspace/normalized/normalized_ast.json
```

**参数**：
- `__init__(ast_path, config_path=None)` - AST 路径、配置路径
- `run()` - 执行标准化

## DOCX 生成（ast_to_docx.py）

```python
import sys
sys.path.insert(0, 'SKILLS/format-normalizer/scripts')
from ast_to_docx import ASTToDocxConverter

converter = ASTToDocxConverter(
    'workspace/normalized/normalized_ast.json',
    'workspace/validated/template_config.json',
    'workspace/input/input.docx'
)
converter.run('workspace/output/formatted.docx')
# 输出: workspace/output/formatted.docx
```

**参数**：
- `__init__(ast_path, template_config_path=None, source_docx_path=None)`
- `run(output_path)` - 生成格式化 DOCX

---

# 处理内容

1. 应用模板配置的字体、字号、行距
2. 标准化标题样式（H1/H2/H3）
3. 插入 TOC 域代码（如启用）
4. 设置页眉页脚（如启用）
5. 段落间距处理（如启用）

---

# 标题格式规则

- 使用模板配置的字体（如黑体）
- 颜色强制黑色（RGB 0,0,0）
- H1 居中，H2/3 左对齐
- 禁止使用 `add_heading()` API

---

# TOC 插入

当 `toc.enabled == true`，目录在文本处理**最后一步**插入：
- 插入位置：封面页之后一节
- 如果有摘要（「摘要」「Abstract」），插入到摘要页之前
- 如果无摘要，插入到第一个 Heading 1 之前
- 目录后加分节符

---

# 分节规则

文档结构：封面 → 分节 → 摘要（如有） → 分节 → 目录 → 分节 → 正文 → 分节 → 参考文献（如有）

| 节 | 内容 | 页眉 | 页脚 |
|----|------|------|------|
| 1 | 封面 | 无 | 无 |
| 2 | 目录 | 无 | 无 |
| 3 | 正文 | 有 | 有（页码从1开始） |
| 4 | 参考文献 | 有 | 有（续正文页码） |

---

# 页眉页脚

- `header.enabled`：写入页眉文本、设置对齐和分隔线
- `footer.enabled`：写入 PAGE 域代码实现自动页码

---

# 错误处理

模板配置错误 → 使用默认值、输出警告
