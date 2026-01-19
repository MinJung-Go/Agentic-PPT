# Agentic-PPT

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个智能 PPT 生成 Agent。基于 GPT/Claude/Deepseek + Gemini 图像生成，可以快速将文本需求转化为专业级 PPT，逻辑清晰、视觉出众。适用于商业、学术等各种场景！

## 核心特性

- **两阶段大纲生成** - 借鉴 NotebookLM，先分析文档结构，再生成精准大纲
- **风格锚定批量生成** - 借鉴 Nano Banana Pro，首页确定风格，后续页面保持一致
- **智能缓存机制** - 大纲和图片缓存，避免重复生成
- **智能错误处理** - 自动降级和重试策略
- **23 种模板预设** - 从商务到时尚，一键切换风格
- **5 个示例内容** - AI技术、商业计划、生活美学、产品发布、学术研究
- **自定义模板** - 通过 YAML 文件轻松创建自己的模板

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/Agentic-PPT.git
cd Agentic-PPT
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```env
DEEPSEEK_API_KEY=your-deepseek-key
GEMINI_API_KEY=your-gemini-key
```

### 4. 运行示例

```bash
python example.py
```

程序会进入交互模式，选择模板和内容即可生成 PPT。

## 代码使用

```python
from ppt_generator import PPTGenerator
import os

# 创建生成器
generator = PPTGenerator(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    provider="deepseek",
    base_url="https://api.deepseek.com/v1"
)

# 生成 PPT
result = generator.generate_ppt(
    reference_text="你的内容文本...",
    style_requirements="科技风格，蓝色主题...",
    output_dir="output",
    template_preset="business_pitch"  # 可选：使用模板预设
)

print(f"生成完成: {result['pptx_file']}")
```

## 模板预设

### 经典商务

| 预设名称 | 中文名称 | 适用场景 |
|---------|---------|---------|
| `business_pitch` | 商业路演 | 融资演示、产品推介、商业计划书 |
| `technical_report` | 技术报告 | 技术分享、研究汇报、项目总结 |
| `product_launch` | 产品发布 | 新品发布会、功能演示、产品介绍 |
| `training` | 培训课程 | 内部培训、教学演示、知识分享 |
| `quarterly_review` | 季度汇报 | 业绩汇报、工作总结、部门复盘 |
| `project_proposal` | 项目提案 | 项目立项、方案提案、需求评审 |
| `company_intro` | 公司介绍 | 企业宣传、合作洽谈、招聘宣讲 |
| `academic` | 学术演讲 | 学术会议、论文答辩、研究报告 |

### 时尚风格

| 预设名称 | 中文名称 | 风格特点 |
|---------|---------|---------|
| `minimal_luxury` | 极简高级 | Apple风格，大量留白，极致简约 |
| `kawaii_cute` | 可爱少女 | 粉嫩甜美风，圆角卡片，可爱插画 |
| `cyberpunk` | 赛博朋克 | 霓虹灯效果，暗黑背景，未来科技感 |
| `morandi` | 莫兰迪色 | 低饱和度高级灰，温柔优雅 |
| `chinese_modern` | 新中式 | 国潮风格，水墨元素 |
| `magazine` | 杂志风 | Editorial设计，大胆字体 |
| `glassmorphism` | 玻璃拟态 | 毛玻璃效果，现代UI风格 |
| `doodle` | 手绘涂鸦 | 手绘风格，趣味活泼 |
| `3d_modern` | 3D立体 | 立体图形，悬浮卡片 |
| `vintage` | 复古怀旧 | 复古色调，文艺风 |

### 特色场景

| 预设名称 | 中文名称 | 风格特点 |
|---------|---------|---------|
| `academic_paper` | 学术论文风 | 清爽学术感，适合论文解读 |
| `xiaohongshu` | 小红书风 | 种草笔记风格，粉嫩配色 |
| `instagram` | INS风 | 欧美博主风格，高级滤镜感 |
| `tech_launch` | 科技发布会 | Apple/小米发布会风格 |
| `muji_minimal` | 日系清新 | MUJI风格，原木色调 |

## 自定义模板

在 `configs/templates/` 目录下添加 YAML 文件即可创建自定义模板：

```yaml
# configs/templates/my_template.yaml
name: "我的模板"
description: "模板描述"
sequence:
  - title
  - content
  - data_dashboard
  - conclusion_cta
narrative: "problem_solution_result"
suggested_slides: 4

style_hints:
  background: "深蓝色渐变背景"
  typography: "现代无衬线字体，标题加粗"
  colors:
    - "#1a1a2e"
    - "#16213e"
    - "#0f3460"
    - "#e94560"
  layout: "左文右图，留白充足"
  visual: "科技感图标，数据可视化"
```

使用自定义模板：

```python
result = generator.generate_ppt(
    reference_text=your_text,
    style_requirements=your_style,
    template_preset="my_template"  # 对应 my_template.yaml
)
```

### 可用的页面类型

| 类型 | 说明 |
|-----|------|
| `title` | 标题页 |
| `toc` | 目录页 |
| `content` | 标准内容页 |
| `problem_solution` | 问题-解决方案对比页 |
| `data_dashboard` | 数据仪表盘 |
| `timeline` | 时间轴 |
| `comparison` | 对比页 |
| `case_study` | 案例研究 |
| `conclusion_cta` | 总结/行动号召 |
| `transition` | 过渡页 |

## 高级用法

### 查看可用预设

```python
for preset in generator.list_template_presets():
    print(f"{preset['key']}: {preset['name']} - {preset['description']}")
```

### 缓存管理

```python
# 查看缓存统计
stats = generator.get_cache_stats()
print(f"大纲缓存: {stats['outline_count']} 个")
print(f"图片缓存: {stats['image_count']} 个")

# 清除过期缓存
generator.clear_cache(older_than_days=7)
```

### 热加载模板

```python
from ppt_generator.template_loader import reload_templates

# 修改 YAML 文件后，重新加载
reload_templates()
```

## 项目结构

```
Agentic-PPT/
├── configs/
│   └── templates/                  # YAML 模板配置文件 (23 个内置模板)
├── ppt_generator/
│   ├── __init__.py                 # 主入口，PPTGenerator 类
│   ├── outline_generator.py        # 两阶段大纲生成
│   ├── document_analyzer.py        # 文档分析器
│   ├── slide_generator_official.py # 幻灯片图片生成 (Google Gemini)
│   ├── batch_generator.py          # 批量生成（风格锚定）
│   ├── prompt_templates.py         # Prompt 模板系统
│   ├── template_loader.py          # YAML 模板加载器
│   ├── cache_manager.py            # 缓存管理
│   ├── error_handler.py            # 智能错误处理
│   └── claude_client.py            # AI 客户端封装
├── example.py                      # 交互式示例
├── requirements.txt                # 依赖列表
├── .env.example                    # 环境变量示例
└── README.md
```

## 核心组件说明

### SlideGenerator（幻灯片生成器）

`slide_generator_official.py` 是项目的核心图像生成组件，负责将大纲内容转化为精美的 PPT 幻灯片图片。

> **说明**：本项目内部版本使用的是 [Nano Banana Pro](https://banana.dev) 服务（基于自有平台接入），生成更稳定。由于内部服务无法公开，开源版本改用 Google Gemini 官方 API 实现相同接口。官方版本尚未经过充分调试优化，生成效果可能不如内部版本稳定，欢迎社区贡献改进！

**技术实现：**
- 使用 **Google Gemini API**（`gemini-2.0-flash-exp-image-generation`）进行图像生成
- 基于 Google 官方 `google-genai` SDK
- 支持异步批量生成，提升效率
- 接口与内部版本完全一致，便于切换

**核心类：**

```python
# ImageGenerationTool - 图像生成工具
class ImageGenerationTool:
    """封装 Gemini API 的图像生成能力"""

    async def gemini_generate(self, params: ImageGenerationParams) -> str:
        """生成单张幻灯片图片"""
        pass

# SlideGenerator - 幻灯片生成器
class SlideGenerator:
    """将大纲转化为幻灯片图片"""

    async def generate_slide_as_image(self, outline_result, slide_index, ...) -> dict:
        """根据大纲生成单张幻灯片"""
        pass
```

**Prompt 工程：**

SlideGenerator 内置了专业的 Prompt 模板，确保生成的幻灯片：
- 布局合理（标题、正文、图表位置精确）
- 中文渲染清晰（避免乱码问题）
- 风格统一（通过风格锚定机制）
- 页码正确显示

**环境变量：**

```bash
GEMINI_API_KEY=your-gemini-api-key  # 必需
```

### 风格锚定机制

借鉴 Nano Banana Pro 的设计理念：

1. **首页生成** - 根据用户需求生成首页，确定整体视觉风格
2. **风格提取** - 从首页提取颜色、字体、布局等风格特征
3. **一致性生成** - 后续页面严格遵循首页风格，保持视觉统一

```python
# batch_generator.py 中的风格锚定逻辑
style_anchor = await self._generate_first_slide(...)  # 生成并锚定首页风格
for slide in remaining_slides:
    await self._generate_with_style(slide, style_anchor)  # 基于锚定风格生成
```

## 技术栈

- **LLM**: DeepSeek / Claude / GPT-4（大纲生成）
- **图像生成**: Google Gemini（幻灯片渲染）
- **PPT 生成**: python-pptx
- **异步处理**: asyncio
- **参数验证**: Pydantic

## TODO

- [x] 更多模板预设 - ins风、小红书风、学术论文风等
- [x] 自定义模板 - 支持用户通过 YAML 定义自己的模板
- [ ] 参考图片风格生成 - 上传参考图片，AI 生成相似风格
- [ ] 模板市场 - 社区模板分享和下载
- [ ] 实时预览 - 生成过程中实时预览效果
- [ ] 多语言支持 - 英文、日文等多语言优化
- [ ] 导出格式 - 支持导出为 PDF、图片序列等
- [ ] 演讲者备注 - 自动生成演讲稿和备注

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT
