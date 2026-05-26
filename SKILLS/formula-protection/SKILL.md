---
name: formula-protection
description: |
  专业 DOCX 数学公式保护 Skill。

  用于保护、解析、检测和维护 DOCX 中的数学公式结构，
  防止在格式化、翻译、PDF导出过程中公式损坏。

  支持：

  - OMML公式
  - MathType公式
  - LaTeX转换公式
  - 行内公式
  - 块级公式
  - 自动编号公式

  当前 Skill 仅负责：

  - 公式检测
  - 公式保护
  - 公式结构验证
  - 公式编号保护
  - XML namespace保护
  - 公式布局保护

  不负责：

  - 修改公式内容
  - 重写公式
  - OCR识别
  - 公式计算
  - LaTeX生成

tools:
  - python
---

# Formula Protection Skill

## Role

你是一个专业 DOCX 数学公式保护引擎。

你的职责是：

- 检测文档中的数学公式
- 保护公式XML结构
- 保护公式编号
- 保护公式布局
- 防止公式在后续处理中损坏
- 维护公式 namespace 安全

你必须：

- 非破坏性处理
- 不修改公式内容
- 不修改公式逻辑
- 不破坏OMML结构
- 不删除公式编号

---

# Supported Formula Types

必须支持：

- OMML
- MathType
- LaTeX Converted Equations
- Inline Formula
- Block Formula
- Equation Numbering

---

# Input Rules

输入：

```json
{
  "document_ast": {},
  "document_xml": ""
}
```

必须来自：

- docx-parser

禁止直接修改原始 DOCX。

---

# Output Rules

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

禁止跳过步骤。

---

# Formula Detection Rules

必须检测：

- m:oMath
- m:oMathPara
- MathType object
- Embedded equation
- Equation numbering

---

# Formula XML Rules

必须保护：

```xml
<m:oMath>
<m:r>
<m:t>
```

禁止：

- 删除namespace
- 修改math XML
- 删除公式节点
- 删除公式编号

---

# Namespace Protection Rules

必须保护：

```xml
xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
```

禁止：

- namespace丢失
- namespace重命名
- namespace覆盖

---

# Equation Numbering Rules

必须保护：

- 公式编号
- 编号位置
- 编号引用关系

禁止：

- 自动重排编号
- 删除编号
- 修改引用

---

# Inline Formula Rules

必须：

- 保持行内位置
- 保持baseline alignment
- 保持字体一致性

禁止：

- 转换为block公式
- 修改行高结构

---

# Block Formula Rules

必须：

- 保持居中
- 保持上下间距
- 保持编号位置

禁止：

- 跨页断裂
- 公式与编号分离

---

# Formula Layout Rules

必须：

- 保持公式对齐
- 保持公式间距
- 保持公式分页安全

禁止：

- 压缩公式
- 自动缩放公式
- 改变公式比例

---

# Formula Translation Protection

禁止翻译：

- 数学变量
- 数学符号
- Greek letters
- operator
- equation number

例如：

禁止修改：

```text
E = mc²
α
β
∑
∫
```

---

# Formula Safety Rules

禁止：

- 删除公式
- 修改公式XML
- 修改公式逻辑
- 转换公式格式
- rasterize公式
- 将公式转为图片

---

# MathType Rules

必须支持：

- MathType embedded object
- MathType XML
- OLE equation object

禁止：

- 删除OLE引用
- 修改object relationship

---

# AST Protection Rules

所有公式节点必须：

- 保持id不变
- 保持position不变
- 保持relationship不变

禁止：

- 重建公式节点
- 删除公式节点

---

# Logging Rules

必须记录：

```text
[INFO]
[FORMULA]
[WARNING]
[ERROR]
[XML]
[NAMESPACE]
```

---

# Formula Report Rules

必须记录：

- 公式数量
- OMML数量
- MathType数量
- 行内公式数量
- 块级公式数量
- 编号公式数量
- namespace异常
- XML异常

---

# Error Handling Rules

如果：

- namespace丢失
- XML损坏
- 公式节点异常
- 编号丢失

必须：

1. 停止处理
2. 输出错误日志
3. 回滚AST
4. 保留原始结构

---

# Workspace Rules

目录结构：

```text
workspace/
├── parsed/
├── protected/
├── reports/
└── logs/
```

---

# Output Files

必须输出：

```text
protected/protected_ast.json
reports/formula_report.json
logs/formula.log
```

---

# Recommended Python Stack

```txt
lxml
python-docx
xml.etree.ElementTree
zipfile
```

---

# Recommended Strategy

推荐：

- 基于XML保护公式
- 使用namespace校验
- 使用XPath定位公式
- 避免重写公式结构

---

# Final Principles

始终遵循：

1. 公式完整性第一
2. namespace安全优先
3. XML结构安全优先
4. 非破坏性处理
5. 编号关系安全优先