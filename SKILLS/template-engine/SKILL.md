---
name: template-engine
description: 专业 DOCX 模板管理与模板映射 Skill。加载、解析、验证和管理论文、公文、用户自定义模板。
tools:
  - python
---

# Template Engine Skill

## Role
专业 DOCX 模板管理引擎。职责：管理格式模板、解析模板配置、验证模板合法性、提供统一模板数据、支持模板继承和fallback。
必须：非破坏性处理、不修改用户模板、不自动覆盖模板、不删除模板字段。

---

# Supported Template Types
必须支持：YAML Template、JSON Template、DOCX Template、Academic Template、Government Template、Custom Template

---

# Input/Output Rules
输入：
```json
{
  "template_name": "",
  "template_path": "",
  "document_type": ""
}
```

输出：
```json
{
  "template_config": {},
  "validated": true,
  "template_report": {}
}
```

---

# Template Directory Rules
默认模板目录：`skills/template-engine/templates/`
用户模板目录：`skills/format-normalizer/custom/`

---

# Processing Pipeline
严格按照以下顺序执行：
1. Scan template directories
2. Detect template type
3. Load template
4. Validate template structure
5. Validate required fields
6. Validate font configuration
7. Validate heading configuration
8. Validate compatibility
9. Build unified config
10. Generate template report
11. Export validated config

---

# Template Selection Rules
Skill 启动时必须：
1. 自动扫描模板目录
2. 自动列出所有模板
3. 询问用户选择模板

禁止：自动默认模板、未经用户确认直接格式化

---

# Template Rules

## YAML Template Rules
必须支持：
```yaml
fonts:
  chinese:
    family: 宋体
```
必须验证：YAML结构合法、字段完整、字段类型正确

## JSON Template Rules
必须支持：
```json
{
  "fonts": {
    "english": {
      "family": "Times New Roman"
    }
  }
}
```
必须验证：JSON合法、字段完整、schema合法

## DOCX Template Rules
必须支持：style extraction、heading extraction、numbering extraction、page layout extraction
禁止：修改原始模板DOCX

---

# Required Template Fields
模板必须包含：fonts、paragraph、heading
否则必须报错。

---

# Template Inheritance Rules
必须支持：
```yaml
extends: chinese_academic.yaml
```
子模板：覆盖父模板字段、保留未覆盖字段

---

# Template Fallback Rules
如果模板缺少字段：
必须：使用默认规则、输出警告日志、记录fallback字段

---

# Font Validation Rules
必须验证：字体名称、fallback字体、字体兼容性
如果字体不存在：必须自动fallback、输出警告

---

# Compatibility Rules
必须兼容：Microsoft Word、WPS、LibreOffice、macOS Word

---

# Security Rules
禁止：自动覆盖模板、删除用户模板、修改原始模板、自动修复模板
仅允许：读取、验证、fallback映射

---

# Unified Config Rules
所有模板最终必须转换为：
```json
{
  "fonts": {},
  "paragraph": {},
  "heading": {},
  "table": {},
  "formula": {},
  "image": {}
}
```

---

# Error Handling
如果：模板损坏、YAML非法、JSON非法、缺失必要字段
必须：停止加载、输出错误日志、保留原始模板、不输出非法配置

---

# Output Files
必须输出：
```text
workspace/validated/template_config.json
workspace/reports/template_report.json
workspace/logs/template_engine.log
```

---

# Final Principles
始终遵循：用户模板优先、模板安全优先、fallback安全优先、非破坏性处理、配置统一性优先
