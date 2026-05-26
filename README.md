# DOCX Master

专业 DOCX 学术论文、公文与技术文档智能处理AGENT。

## 功能特性

- **中文论文格式化** - 自动标准化中文学术论文排版
- **英文论文格式化** - 支持 IEEE、ACM 等英文论文格式
- **公文格式化** - 符合国家标准的公文排版
- **用户自定义模板** - 支持 YAML/JSON 自定义格式模板
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
3. 处理完成后，文件位于 `workspace/output/`

## 项目结构

```
doc-from-master/
├── AGENT.md                    # Agent 配置文件
├── SKILLS/                     # 技能模块
│   ├── docx-parser/            # DOCX 结构解析
│   ├── xml-safety/             # XML 安全校验
│   ├── formula-protection/     # 数学公式保护
│   ├── template-engine/        # 模板管理
│   ├── font-manager/           # 字体兼容管理
│   ├── format-normalizer/      # 格式标准化
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

Phase 3: 格式化与优化
    format-normalizer → image-layout

Phase 4: 后处理
    translation-engine (可选)
    pdf-export (可选)
```

## 模板说明

系统内置模板位于 `SKILLS/format-normalizer/custom/`:

- `chinese_academic.yaml` - 中文学术论文
- `english_academic.yaml` - 英文论文

支持自定义 YAML/JSON 模板。

## 注意事项

- 系统采用非破坏性处理，不会修改原始文件
- 所有操作均可回滚
- 大型文档 (>200页) 自动启用分块处理

## 许可证

GPL 3.0