# DOCX Master

专业 DOCX 学术论文、公文与技术文档智能处理AGENT。

## 功能特性

- **中文论文格式化** - 自动标准化中文学术论文排版（GB/T 7713.1-2006）
- **英文论文格式化** - 支持 APA、IEEE、ACM 等英文论文格式
- **公文格式化** - 符合国家标准的公文排版（GB/T 9704-2012）
- **用户自定义模板** - 支持 YAML/JSON 自定义格式模板
- **智能标题识别** - 自动验证并修正误标为标题的正文段落
- **设计预览与确认** - 浏览器中预览封面页、目录页、页眉页脚和正文样式，支持在线编辑
- **自动生成目录** - 使用 Word TOC 域代码自动生成目录，包含页码、层级缩进和前导点
- **页眉页脚管理** - 自定义页眉文本、分隔线和页码格式（阿拉伯/罗马/中文数字）
- **段落间距控制** - 可选「段落之间空行分隔」，灵活控制正文排版风格
- **中英互译** - 保持文档结构的智能翻译
- **数学公式保护** - 完整保留 OMML、MathType 公式
- **图片布局优化** - 自动调整图片位置和大小
- **字体兼容管理** - 跨平台字体检测与 fallback
- **PDF 导出** - 高质量 PDF 输出
- **XML 安全保护** - 防止 DOCX 结构损坏

## 系统要求

- Python 3.10+
- Windows 10/11 (推荐)
- Microsoft Word 或 LibreOffice (PDF 导出需要)

## 快速开始

### 1. 安装依赖

```bash
# Windows
install_requirements.bat

# 或手动安装
pip install -r requirements.txt
```

### 2. 使用方法

1. 将 DOCX 文件放入 `workspace/input/`
2. 运行 Agent，按提示选择处理选项
3. 在浏览器预览界面中确认：
   - 封面页设计（保留或重新设计）
   - 目录页配置（自动生成、标题样式、最大级别）
   - 页眉页脚设置（文本、字体、对齐、页码格式）
   - 正文样式（字体、字号、行距、缩进）
   - 段落间距（是否空行分隔）
4. 确认后系统自动完成格式标准化
5. 处理完成后，文件位于 `workspace/output/`
6. 在 Word 中按 `Ctrl+A` 后按 `F9` 更新域以生成目录页码

## 项目结构

```
doc-from-master/
├── AGENT.md                    # Agent 配置文件
├── SKILLS/                     # 技能模块
│   ├── docx-parser/            # DOCX 结构解析（含封面/目录检测）
│   ├── xml-safety/             # XML 安全校验
│   ├── formula-protection/     # 数学公式保护
│   ├── template-engine/        # 模板管理
│   ├── font-manager/           # 字体兼容管理
│   ├── format-normalizer/      # 格式标准化（含 TOC 域/页眉页脚/段落间距）
│   ├── preview-design/         # 设计预览与用户确认（Web 界面）
│   ├── image-layout/           # 图片布局优化
│   ├── translation-engine/     # 中英互译
│   └── pdf-export/             # PDF 导出
├── workspace/                  # 工作区 (运行时创建)
│   ├── input/                  # 输入文件
│   ├── output/                 # 输出文件
│   └── reports/                # 处理报告
├── requirements.txt            # Python 依赖
└── install_requirements.bat    # 依赖安装脚本
```

## 处理流程

```text
Phase 1: 解析与验证
    docx-parser → xml-safety

Phase 2: 保护与配置
    formula-protection
    template-engine
    font-manager

Phase 3: 设计预览与用户确认（浏览器交互）
    preview-design → 用户确认封面页/目录页/页眉页脚/段落间距/样式

Phase 4: 格式化与优化
    format-normalizer → image-layout

Phase 5: 后处理
    translation-engine (可选)
    pdf-export (可选)
```

## 模板说明

系统内置模板位于 `SKILLS/format-normalizer/custom/`:

| 模板文件 | 标准 | 说明 |
|---------|------|------|
| `chinese_academic.yaml` | GB/T 7713.1-2006 | 中文学术论文 |
| `english_academic.yaml` | APA 第 7 版 | 英文论文 |

### 中文学术论文标准 (GB/T 7713.1-2006)
- 页面：A4，页边距 上25.4mm 下25.4mm 左31.7mm 右25.4mm
- 正文：小4号宋体，1.5倍行距
- 一级标题：4号黑体，居中
- 二级标题：小4号黑体，左对齐
- 三级标题：小4号宋体，左对齐

### 英文论文标准 (APA 第 7 版)
- 页面：A4/Letter，页边距 2.54cm (1英寸)
- 正文：12pt Times New Roman，双倍行距
- 标题：12pt Times New Roman，加粗
- 首行缩进：0.5英寸 (1.27cm)

支持自定义 YAML/JSON 模板。

## 最近更新

### v1.2.0 (2025-05-27)
- **智能标题验证**：自动检测并修正误标为标题的正文段落（如过长文本、以标点结尾等）
- **改进目录检测**：支持识别 "目录" 样式名的段落，正确识别 TOC 区域
- **修复图片丢失**：解决删除所有节后图片处理失败的问题
- **模板标准化**：更新中文/英文论文模板以符合国家标准

### v1.1.0
- 支持 4 个独立节（封面、目录、正文、引用）
- 页码从正文第一页开始
- 目录页自动生成 TOC 域代码

## 注意事项

- 系统采用非破坏性处理，不会修改原始文件
- 所有操作均可回滚
- 大型文档 (>200页) 自动启用分块处理
- 目录页使用 Word TOC 域代码生成，打开文档后需按 `Ctrl+A` 再按 `F9` 更新域以显示页码
- 页眉页脚通过 Word 底层 XML 写入，兼容 WPS 和 LibreOffice

## 许可证

GPL 3.0