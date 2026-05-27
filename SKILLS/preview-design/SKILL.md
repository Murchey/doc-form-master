---
name: preview-design
description: 专业 DOCX 文档设计预览与编辑 Skill。在浏览器中预览封面页、目录页、页眉页脚和正文样式，允许用户在线编辑和确认。
tools:
  - python
  - flask
---

# Preview Design Skill

## Role
专业 DOCX 文档设计预览引擎。职责：读取文档 AST 和模板配置、在浏览器中渲染文档设计预览、展示封面页/目录页/页眉页脚的设计、允许用户在线编辑样式参数、收集用户确认结果。
必须：不修改原始文档、不修改 AST、不修改模板配置文件、仅在用户确认后将配置传递给后续 Skill。

---

# Core Responsibilities
必须预览和编辑：封面页设计、目录页设计、页眉页脚设计、正文样式、标题样式、表格样式、图片布局

---

# Input/Output Rules
输入：
```json
{
  "ast_path": "",
  "template_config_path": "",
  "source_docx_path": ""
}
```
必须来自：docx-parser（AST）、template-engine（模板配置）

输出：
```json
{
  "user_confirmed": true,
  "cover_preserved": true,
  "toc_preserved": true,
  "edited_config": {
    "fonts": {},
    "heading": {},
    "paragraph": {
      "line_spacing": 1.5,
      "first_indent": 2,
      "paragraph_spacing": false
    },
    "page": {},
    "toc": {
      "enabled": true,
      "title": "目  录",
      "title_font": "黑体",
      "title_size": 16,
      "entry_font": "宋体",
      "entry_size": 12,
      "max_level": 3,
      "indent_step": 2,
      "dot_leaders": true
    },
    "header": {
      "enabled": true,
      "text": "XX大学学报",
      "font": "宋体",
      "size": 9,
      "alignment": "center",
      "separator_line": true
    },
    "footer": {
      "enabled": true,
      "page_number_format": "arabic",
      "font": "宋体",
      "size": 9,
      "alignment": "center"
    }
  },
  "design_preview_url": ""
}
```

---

# Processing Pipeline
严格按照以下顺序执行：
1. Load AST
2. Load template config
3. Detect cover page sections
4. Detect TOC sections
5. Detect header/footer
6. Extract all headings for TOC preview
7. Generate preview HTML（含封面/目录/页眉页脚/正文）
8. Start local web server
9. **Wait 2-3 seconds for server to fully start**
10. Open browser for user
11. Wait for user confirmation
12. Return user choices（含 toc/header/footer 配置）

---

# Preview Sections

## Cover Page Preview
必须展示：文档标题样式、作者信息样式、机构信息样式、日期样式、封面页布局
用户可以：确认保留原始封面设计、修改标题字体/字号、修改对齐方式

### 封面设计功能
当文档没有检测到封面页，或用户选择"重新设计封面"时，提供以下设计选项：

**大标题设置：**
- 标题文本（如：课程作业、毕业论文等）
- 标题字体（默认：黑体）
- 标题字号（默认：22pt）
- 标题对齐方式（居中/左对齐）
- 标题加粗（默认：是）

**个人信息表：**
- 支持添加多个信息项（如：学号、姓名、学院、专业、指导教师、日期等）
- 每项可设置标签和值
- 字体和字号配置
- 对齐方式

**学校标志：**
- 支持上传学校logo图片
- 设置logo大小和位置
- 可选择是否显示

**封面布局：**
- 垂直居中布局
- 自定义间距
- 页面边距设置

## TOC Page Preview
必须展示：已有目录页（如果文档中存在）、自动生成目录的预览（基于文档所有标题）、目录标题样式、最大标题级别选择
用户可以：确认保留原始目录设计、选择自动生成目录页、修改目录标题文本、修改标题字体和字号、选择包含的标题级别

目录生成采用 Word 内置 TOC 域代码（`TOC \o "1-N" \h \z \u`），Word 打开文档后会自动：按层级缩进排列目录条目、生成正确的页码、添加带前导点的制表符、支持超链接跳转
用户在 Word 中按 Ctrl+A 后按 F9 即可更新域以刷新目录内容。

## Header/Footer Preview
必须展示：页眉文本和样式预览（含分隔线）、页脚页码样式预览（含格式选择）、以页面布局模拟的方式直观展示

用户可以：
**页眉：** 开关页眉、修改页眉文本、修改字体/字号、修改对齐方式（左/中/右）、开关分隔线
**页脚：** 开关页脚页码、选择页码格式（阿拉伯数字/罗马数字/中文数字）、修改字体/字号、修改对齐方式（左/中/右）

## Body Style Preview
必须展示：正文字体/字号、行距/缩进、各级标题样式、段落对齐、段落之间是否空行分隔
用户可以：修改所有正文样式参数、勾选「段落之间空行分隔」

---

# Web Server Rules
必须：使用本地 HTTP 服务器、**等待服务器完全启动后再打开浏览器**、支持样式实时预览、支持用户确认提交、服务器在确认后自动关闭
端口范围：8765-8780

## 浏览器启动时序（重要）
必须确保服务器完全启动后再打开浏览器，否则浏览器会显示空白页面或连接失败。
推荐实现：
```python
import time
# 启动服务器线程
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()
# 等待服务器完全启动
time.sleep(2)
# 打开浏览器
webbrowser.open(url)
```

---

# Security Rules
禁止：访问外部网络、修改源文件、修改 AST 文件、持久化存储用户数据
仅允许：读取 AST 和配置、本地 HTTP 服务、临时文件创建

---

# Final Principles
始终遵循：用户确认优先、非破坏性预览、实时反馈、安全隔离
