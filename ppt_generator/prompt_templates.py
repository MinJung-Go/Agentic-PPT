"""
PPT Prompt 模板系统 - 借鉴 NotebookLM 和 Nano Banana Pro 最佳实践

提供结构化的 Prompt 模板，确保生成高质量、风格一致的 PPT 页面。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from .template_loader import get_template_presets


@dataclass
class SlideTemplate:
    """幻灯片模板"""
    type_name: str
    structure: str
    visual_hierarchy: str
    emotional_tone: str
    layout_zones: Dict[str, str]
    design_rules: List[str]


class PromptTemplateSystem:
    """结构化 Prompt 模板系统"""

    def __init__(self):
        self.templates = self._init_templates()
        self.narrative_structures = self._init_narrative_structures()
        self.style_modifiers = self._init_style_modifiers()
        self.chinese_rendering_rules = self._init_chinese_rendering_rules()
        self.page_number_style = self._init_page_number_style()

    def _init_templates(self) -> Dict[str, SlideTemplate]:
        """初始化幻灯片类型模板"""
        return {
            # 标题页 - Hero Title
            "title": SlideTemplate(
                type_name="Hero Title Slide",
                structure="Problem Statement - 制造好奇心缺口，3秒抓住注意力",
                visual_hierarchy="60% 主标题（居中） + 20% 副标题 + 20% 背景视觉",
                emotional_tone="inspiring, confident, forward-looking, prestigious",
                layout_zones={
                    "title": "middle-center, large bold text",
                    "subtitle": "below title, medium text",
                    "background": "sophisticated gradient or abstract pattern",
                    "decoration": "subtle particle effects or geometric shapes"
                },
                design_rules=[
                    "标题字数不超过12个字",
                    "副标题补充说明，不超过20字",
                    "背景使用深色渐变或抽象图案",
                    "留白充足，突出标题"
                ]
            ),

            # 目录页 - Table of Contents
            "toc": SlideTemplate(
                type_name="Table of Contents",
                structure="清晰路线图，降低认知负荷",
                visual_hierarchy="20% 标题 + 70% 目录项 + 10% 页码",
                emotional_tone="clear, organized, professional",
                layout_zones={
                    "title": "top-left or top-center",
                    "items": "middle area, 3-5 items with icons",
                    "current_indicator": "highlight current section",
                    "page_number": "bottom-right"
                },
                design_rules=[
                    "目录项 3-5 个为宜",
                    "每项配图标，增强识别",
                    "当前章节高亮显示",
                    "保持视觉平衡"
                ]
            ),

            # 问题-解决方案页 - Problem-Solution
            "problem_solution": SlideTemplate(
                type_name="Problem-Solution Comparison",
                structure="左侧痛点可视化 → 中间转换箭头 → 右侧方案展示",
                visual_hierarchy="45% 问题区 + 10% 过渡 + 45% 方案区",
                emotional_tone="empathetic, hopeful, transformative",
                layout_zones={
                    "problem": "left side, pain point with red/orange accent",
                    "transition": "center, arrow or transformation symbol",
                    "solution": "right side, benefit with green/blue accent",
                    "title": "top-center spanning both sides"
                },
                design_rules=[
                    "问题用暖色调（红/橙）暗示",
                    "方案用冷色调（蓝/绿）表示",
                    "中间过渡元素清晰",
                    "文字精简，图标主导"
                ]
            ),

            # 数据仪表盘 - Data Dashboard
            "data_dashboard": SlideTemplate(
                type_name="Data Dashboard",
                structure="核心指标（大数字居中）+ 支撑数据（环绕）+ 洞察文字",
                visual_hierarchy="40% 核心数据 + 40% 支撑图表 + 20% 说明",
                emotional_tone="authoritative, clear, data-driven",
                layout_zones={
                    "key_metric": "center-top, large bold number",
                    "supporting_charts": "middle area, 2-3 small charts",
                    "insight": "bottom, brief insight text",
                    "labels": "clear data labels on all elements"
                },
                design_rules=[
                    "核心数据用超大字号",
                    "图表简洁，无3D效果",
                    "颜色编码一致",
                    "数据标签清晰可读"
                ]
            ),

            # 时间轴 - Timeline
            "timeline": SlideTemplate(
                type_name="Timeline / Process Flow",
                structure="3-5个里程碑横向排列，当前位置高亮",
                visual_hierarchy="15% 标题 + 70% 时间轴 + 15% 说明",
                emotional_tone="progressive, forward-moving, structured",
                layout_zones={
                    "title": "top-left or top-center",
                    "timeline": "middle, horizontal flow left-to-right",
                    "milestones": "3-5 nodes with icons and labels",
                    "current": "highlighted current position"
                },
                design_rules=[
                    "里程碑 3-5 个最佳",
                    "使用连接线表示流程",
                    "当前阶段视觉突出",
                    "每个节点配简短标签"
                ]
            ),

            # 对比页 - Comparison
            "comparison": SlideTemplate(
                type_name="Two-Column Comparison",
                structure="左右对比，优劣势清晰展示",
                visual_hierarchy="10% 标题 + 45% 左侧 + 45% 右侧",
                emotional_tone="objective, analytical, decisive",
                layout_zones={
                    "title": "top-center",
                    "left_column": "left 45%, with header",
                    "right_column": "right 45%, with header",
                    "vs_indicator": "center divider or VS symbol"
                },
                design_rules=[
                    "两列结构对称",
                    "使用对比色区分",
                    "要点数量对等",
                    "中间分隔清晰"
                ]
            ),

            # 案例研究 - Case Study
            "case_study": SlideTemplate(
                type_name="Case Study / Success Story",
                structure="客户背景 + 挑战 + 解决方案 + 成果",
                visual_hierarchy="30% 案例图片 + 50% 内容 + 20% 成果数据",
                emotional_tone="credible, inspiring, results-focused",
                layout_zones={
                    "image": "left or top, case visual",
                    "content": "right or bottom, story elements",
                    "metrics": "highlighted success metrics",
                    "quote": "optional customer quote"
                },
                design_rules=[
                    "真实案例图片增强可信度",
                    "成果用数据量化",
                    "客户引言加分",
                    "故事线清晰"
                ]
            ),

            # 总结/行动号召 - Conclusion CTA
            "conclusion_cta": SlideTemplate(
                type_name="Conclusion with Call-to-Action",
                structure="3个要点回顾 + 明确行动号召 + 联系方式",
                visual_hierarchy="30% 要点 + 40% CTA + 30% 联系信息",
                emotional_tone="confident, memorable, actionable",
                layout_zones={
                    "takeaways": "top or left, 3 key points",
                    "cta": "center, clear call-to-action",
                    "contact": "bottom, contact information",
                    "next_steps": "what to do next"
                },
                design_rules=[
                    "要点不超过3个",
                    "CTA 动词开头，明确具体",
                    "联系方式完整",
                    "设计有力量感"
                ]
            ),

            # 标准内容页 - Standard Content
            "content": SlideTemplate(
                type_name="Standard Content Slide",
                structure="标题 + 3-5个要点 + 支撑视觉",
                visual_hierarchy="20% 标题 + 50% 内容 + 30% 视觉",
                emotional_tone="clear, informative, professional",
                layout_zones={
                    "title": "top-left, clear heading",
                    "content": "left or center, bullet points",
                    "visual": "right or bottom, supporting image/icon",
                    "page_number": "bottom-right"
                },
                design_rules=[
                    "一页一主题",
                    "要点 3-5 个",
                    "每点不超过15字",
                    "配图增强理解"
                ]
            ),

            # 过渡页 - Transition
            "transition": SlideTemplate(
                type_name="Section Transition",
                structure="章节标题 + 简短引言",
                visual_hierarchy="70% 章节标题 + 30% 背景",
                emotional_tone="transitional, refreshing, preparatory",
                layout_zones={
                    "section_title": "center, large text",
                    "subtitle": "below title, brief intro",
                    "background": "distinct from content slides"
                },
                design_rules=[
                    "与标题页风格呼应",
                    "承上启下作用",
                    "视觉上的\"呼吸\"",
                    "不宜信息过多"
                ]
            )
        }

    def _init_narrative_structures(self) -> Dict[str, List[str]]:
        """初始化叙事结构模板"""
        return {
            # 问题-解决方案-结果 (最常用)
            "problem_solution_result": [
                "title",          # 开场：抛出问题或愿景
                "toc",            # 路线图
                "content",        # 问题/现状分析
                "problem_solution",  # 解决方案对比
                "content",        # 方案详情
                "data_dashboard", # 数据支撑
                "case_study",     # 案例验证
                "conclusion_cta"  # 总结行动
            ],

            # 时间线叙事
            "chronological": [
                "title",
                "toc",
                "timeline",
                "content",
                "content",
                "content",
                "conclusion_cta"
            ],

            # 对比分析
            "comparison_analysis": [
                "title",
                "toc",
                "comparison",
                "data_dashboard",
                "content",
                "conclusion_cta"
            ],

            # 故事驱动
            "story_driven": [
                "title",
                "content",        # 背景设定
                "problem_solution",  # 冲突
                "timeline",       # 发展
                "data_dashboard", # 高潮（成果）
                "conclusion_cta"  # 结局
            ]
        }

    def _init_style_modifiers(self) -> Dict[str, Dict[str, str]]:
        """初始化风格修饰器"""
        return {
            "corporate": {
                "colors": "navy blue, white, subtle gold accents",
                "fonts": "clean sans-serif, professional",
                "mood": "trustworthy, established, premium",
                "background": "subtle gradients, geometric patterns"
            },
            "tech": {
                "colors": "dark backgrounds, neon accents, gradients",
                "fonts": "modern, geometric, tech-forward",
                "mood": "innovative, cutting-edge, futuristic",
                "background": "circuit patterns, abstract tech visuals"
            },
            "creative": {
                "colors": "vibrant, bold color combinations",
                "fonts": "expressive, varied weights",
                "mood": "dynamic, inspiring, unconventional",
                "background": "artistic, textured, unique"
            },
            "minimal": {
                "colors": "black, white, single accent color",
                "fonts": "thin, elegant, lots of whitespace",
                "mood": "sophisticated, clean, focused",
                "background": "solid colors, minimal decoration"
            },
            "academic": {
                "colors": "muted, professional, conservative",
                "fonts": "serif or classic sans-serif",
                "mood": "credible, scholarly, structured",
                "background": "clean, distraction-free"
            }
        }

    def get_template(self, slide_type: str) -> SlideTemplate:
        """获取指定类型的模板"""
        # 映射常见的中文类型名到英文键
        type_mapping = {
            "标题页": "title",
            "目录页": "toc",
            "内容页": "content",
            "数据页": "data_dashboard",
            "时间轴": "timeline",
            "对比页": "comparison",
            "案例页": "case_study",
            "总结页": "conclusion_cta",
            "过渡页": "transition",
            "问题解决": "problem_solution"
        }

        # 尝试直接匹配或通过映射匹配
        key = type_mapping.get(slide_type, slide_type.lower().replace(" ", "_"))
        return self.templates.get(key, self.templates["content"])

    def build_image_prompt(
        self,
        slide_info: Dict,
        slide_index: int,
        total_slides: int,
        style_requirements: str,
        brand_colors: Dict = None,
        style_hints: Dict = None
    ) -> str:
        """
        构建图片生成的增强版 Prompt

        Args:
            slide_info: 幻灯片信息
            slide_index: 当前页索引
            total_slides: 总页数
            style_requirements: 风格要求
            brand_colors: 品牌色彩（可选）
            style_hints: 模板预设的风格提示（可选）

        Returns:
            结构化的图片生成 Prompt
        """
        slide_type = slide_info.get("slide_type", "content")
        template = self.get_template(slide_type)

        # 确定叙事位置
        narrative_position = self._determine_narrative_position(slide_index, total_slides)

        # 获取风格修饰
        style_modifier = self._match_style_modifier(style_requirements)

        # 构建结构化 Prompt
        prompt_parts = [
            f"Create a professional PPT slide image (16:9 aspect ratio).",
        ]

        # 【关键】将模板预设风格提示放在最前面，优先级最高
        if style_hints:
            prompt_parts.extend([
                "",
                "=" * 60,
                "[CRITICAL - PRESET STYLE - HIGHEST PRIORITY]",
                "=" * 60,
                "You MUST follow these style requirements EXACTLY:",
                f"  ★ Background: {style_hints.get('background', '')}",
                f"  ★ Typography: {style_hints.get('typography', '')}",
                f"  ★ Color Palette: {', '.join(style_hints.get('colors', []))}",
                f"  ★ Layout Style: {style_hints.get('layout', '')}",
                f"  ★ Visual Elements: {style_hints.get('visual', '')}"
            ])
            if style_hints.get('special'):
                prompt_parts.append(f"  ★ Special: {style_hints.get('special')}")
            prompt_parts.extend([
                "",
                "⚠️ WARNING: The above style MUST be strictly followed!",
                "⚠️ Do NOT deviate from these visual requirements!",
                "=" * 60,
            ])

        prompt_parts.extend([
            "",
            f"[SLIDE TYPE] {template.type_name}",
            f"[PAGE] {slide_index + 1} of {total_slides}",
            f"[NARRATIVE ROLE] {narrative_position}",
            "",
            f"[STRUCTURE]",
            f"{template.structure}",
            "",
            f"[VISUAL HIERARCHY]",
            f"{template.visual_hierarchy}",
            "",
            f"[LAYOUT ZONES]"
        ])

        for zone, desc in template.layout_zones.items():
            prompt_parts.append(f"  - {zone}: {desc}")

        prompt_parts.extend([
            "",
            f"[CONTENT]",
            f"  Title: {slide_info.get('title', '')}",
        ])

        # 添加关键点（限制数量）
        key_points = slide_info.get("key_points", [])[:3]
        if key_points:
            prompt_parts.append(f"  Key Points:")
            for i, point in enumerate(key_points, 1):
                prompt_parts.append(f"    {i}. {point}")

        prompt_parts.extend([
            "",
            f"[STYLE]",
            f"  Theme: {style_requirements}",
            f"  Mood: {template.emotional_tone}"
        ])

        if style_modifier:
            prompt_parts.extend([
                f"  Colors: {style_modifier['colors']}",
                f"  Fonts: {style_modifier['fonts']}",
                f"  Background: {style_modifier['background']}"
            ])

        # style_hints 已经在 prompt 开头添加，这里只做重复强调
        if style_hints:
            prompt_parts.extend([
                "",
                "[STYLE REMINDER - REFER TO TOP SECTION]",
                "Apply the preset style defined at the beginning of this prompt!"
            ])

        if brand_colors:
            prompt_parts.extend([
                "",
                f"[BRAND COLORS]",
                f"  Primary: {brand_colors.get('primary', '#1e3c72')}",
                f"  Secondary: {brand_colors.get('secondary', '#2196F3')}",
                f"  Accent: {brand_colors.get('accent', '#FF9800')}"
            ])

        prompt_parts.extend([
            "",
            f"[DESIGN RULES]"
        ])
        for rule in template.design_rules:
            prompt_parts.append(f"  - {rule}")

        # 添加中文渲染要求
        prompt_parts.extend([
            "",
            f"[CHINESE TEXT RENDERING - CRITICAL]",
            f"  Font: {self.chinese_rendering_rules['font_requirements']['style']}",
            "  Requirements:",
            "  - All Chinese text MUST be crisp, clear, and highly legible",
            "  - Use proper anti-aliasing for smooth text edges",
            "  - High contrast between text and background",
            "  - Consistent font weight: bold for titles, medium for body",
            "  - Proper character spacing (not cramped)",
            "  - Line height 1.5-1.8x for readability",
            "  - NO blurry, distorted, or low-quality text"
        ])

        # 添加统一页码样式
        prompt_parts.extend([
            "",
            f"[PAGE NUMBER - MUST BE CONSISTENT]",
            f"  Position: {self.page_number_style['position']}",
            f"  Format: {slide_index + 1} / {total_slides}",
            "  Style:",
            f"  - Small font (10-12pt), regular weight",
            f"  - Subtle gray color (#666666) or theme-matched",
            f"  - 70-80% opacity",
            f"  - 8-12px padding from slide edges",
            "  CRITICAL: Use EXACT same style on EVERY slide - no variation!"
        ])

        prompt_parts.extend([
            "",
            f"[AVOID]",
            "  - Cluttered layouts with too many elements",
            "  - Excessive text that's hard to read",
            "  - Inconsistent styling or colors",
            "  - Low-quality or pixelated graphics",
            "  - 3D effects on charts or elements",
            "  - Blurry or illegible Chinese characters",
            "  - Inconsistent page number placement or style"
        ])

        return "\n".join(prompt_parts)

    def _determine_narrative_position(self, slide_index: int, total_slides: int) -> str:
        """确定当前页在叙事结构中的位置"""
        position_ratio = slide_index / max(total_slides - 1, 1)

        if slide_index == 0:
            return "Opening - 吸引注意力，建立期待"
        elif position_ratio < 0.3:
            return "Setup - 铺垫背景，定义问题"
        elif position_ratio < 0.7:
            return "Development - 展开论述，提供证据"
        elif slide_index == total_slides - 1:
            return "Closing - 总结要点，号召行动"
        else:
            return "Climax - 核心论点，关键转折"

    def _match_style_modifier(self, style_requirements: str) -> Optional[Dict]:
        """根据风格要求匹配修饰器"""
        style_lower = style_requirements.lower()

        for style_name, modifier in self.style_modifiers.items():
            if style_name in style_lower:
                return modifier

        # 关键词匹配
        if any(kw in style_lower for kw in ["企业", "商务", "公司", "corporate"]):
            return self.style_modifiers["corporate"]
        elif any(kw in style_lower for kw in ["科技", "技术", "互联网", "tech", "ai"]):
            return self.style_modifiers["tech"]
        elif any(kw in style_lower for kw in ["创意", "艺术", "设计", "creative"]):
            return self.style_modifiers["creative"]
        elif any(kw in style_lower for kw in ["简约", "极简", "minimal", "simple"]):
            return self.style_modifiers["minimal"]
        elif any(kw in style_lower for kw in ["学术", "研究", "论文", "academic"]):
            return self.style_modifiers["academic"]

        return self.style_modifiers["corporate"]  # 默认企业风格

    def _init_chinese_rendering_rules(self) -> Dict:
        """初始化中文文本渲染规则 - 借鉴 Nano Banana Pro 多语言渲染"""
        return {
            "font_requirements": {
                "primary": "Noto Sans SC, Microsoft YaHei, PingFang SC",
                "fallback": "Source Han Sans CN, WenQuanYi Micro Hei",
                "style": "clean, modern, highly legible Chinese font"
            },
            "text_rendering": {
                "anti_aliasing": "smooth, no jagged edges",
                "contrast": "high contrast between text and background",
                "weight": "medium weight for body, bold for titles",
                "spacing": "proper character spacing (not too tight)"
            },
            "layout_rules": {
                "line_height": "1.5x to 1.8x for Chinese text",
                "paragraph_spacing": "generous spacing between blocks",
                "margins": "adequate margins to prevent text crowding"
            },
            "quality_checks": [
                "Chinese characters must be crisp and clear",
                "No blurry or distorted text",
                "Consistent font style throughout",
                "Proper punctuation rendering",
                "No character overlap or collision"
            ]
        }

    def _init_page_number_style(self) -> Dict:
        """初始化统一的页码样式规范"""
        return {
            "position": "bottom-right corner",
            "format": "{current} / {total}",
            "style": {
                "font_size": "small, 10-12pt equivalent",
                "font_weight": "regular",
                "color": "subtle gray (#666666) or match theme accent",
                "opacity": "70-80% for subtlety"
            },
            "container": {
                "background": "none or very subtle rounded rectangle",
                "padding": "8-12px from edges",
                "alignment": "right-aligned"
            },
            "consistency_rules": [
                "EXACT same position on every slide",
                "EXACT same font size and style",
                "EXACT same color and opacity",
                "NO variation in format or placement",
                "Visible but not distracting"
            ]
        }

    def suggest_narrative_structure(self, doc_analysis: Dict) -> List[str]:
        """根据文档分析结果推荐叙事结构"""
        doc_type = doc_analysis.get("document_type", "").lower()
        suggested = doc_analysis.get("suggested_narrative", "").lower()

        if "时间" in suggested or "历程" in suggested or "发展" in suggested:
            return self.narrative_structures["chronological"]
        elif "对比" in suggested or "比较" in suggested:
            return self.narrative_structures["comparison_analysis"]
        elif "故事" in suggested or "案例" in suggested:
            return self.narrative_structures["story_driven"]
        else:
            return self.narrative_structures["problem_solution_result"]

    # ==================== 预设模板组合 ====================

    def get_preset(self, preset_name: str) -> Optional[Dict]:
        """
        获取预设模板组合

        Args:
            preset_name: 预设名称

        Returns:
            预设配置字典，包含 name, description, sequence, narrative
        """
        return get_template_presets().get(preset_name)

    def list_presets(self) -> List[Dict]:
        """
        列出所有可用预设

        Returns:
            预设列表，每项包含 key, name, description
        """
        return [
            {
                "key": key,
                "name": preset.get("name", key),
                "description": preset.get("description", "")
            }
            for key, preset in get_template_presets().items()
        ]

    def get_preset_sequence(self, preset_name: str) -> List[str]:
        """
        获取预设的模板序列

        Args:
            preset_name: 预设名称

        Returns:
            模板类型序列列表
        """
        preset = self.get_preset(preset_name)
        return preset.get("sequence", []) if preset else []

    def get_preset_narrative(self, preset_name: str) -> str:
        """
        获取预设推荐的叙事结构

        Args:
            preset_name: 预设名称

        Returns:
            叙事结构名称
        """
        preset = self.get_preset(preset_name)
        return preset.get("narrative", "problem_solution_result") if preset else "problem_solution_result"
