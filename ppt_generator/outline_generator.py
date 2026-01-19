"""
PPT大纲生成器 - 负责生成结构化的PPT大纲

借鉴 NotebookLM 的两阶段生成理念：
1. 第一阶段：文档分析（理解结构）
2. 第二阶段：大纲生成（基于分析结果）
"""

import json
import logging
from typing import Dict, List, Optional

from .document_analyzer import DocumentAnalyzer
from .template_loader import get_template_presets

logger = logging.getLogger(__name__)


class OutlineGenerator:
    """
    PPT大纲生成器

    支持两种生成模式：
    1. 单阶段生成（向后兼容）：直接从文本生成大纲
    2. 两阶段生成（推荐）：先分析文档，再生成大纲
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.slide_templates = self._init_slide_templates()
        self.document_analyzer = DocumentAnalyzer(llm_client)

    def generate_outline(
        self,
        reference_text: str,
        style_requirements: str,
        model: str = "gpt-4",
        template_preset: str = None
    ) -> Dict:
        """
        生成PPT大纲

        Args:
            reference_text: 参考文本内容
            style_requirements: 风格要求
            model: 使用的模型
            template_preset: 模板预设名称（可选）

        Returns:
            Dict: 结构化的PPT大纲
        """
        system_prompt = self._get_system_prompt(template_preset)
        user_prompt = self._build_user_prompt(reference_text, style_requirements, template_preset)

        result = self.llm_client.generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            expected_structure="json",
            model=model,
            max_tokens=8000
        )

        # 验证并修复结果
        result = self._validate_and_fix_result(result, reference_text, style_requirements)

        # 后处理：添加推断的关系和建议
        result = self._post_process(result)

        return result

    def generate_outline_two_stage(
        self,
        reference_text: str,
        style_requirements: str,
        audience_profile: Dict = None,
        brand_guidelines: Dict = None,
        context_hints: Dict = None,
        model: str = "gpt-4",
        template_preset: str = None
    ) -> Dict:
        """
        两阶段大纲生成（推荐）- 借鉴 NotebookLM 理念

        阶段1：文档分析 - 深度理解文档结构
        阶段2：大纲生成 - 基于分析结果生成高质量大纲

        Args:
            reference_text: 参考文本内容
            style_requirements: 风格要求
            audience_profile: 目标受众信息（可选）
            brand_guidelines: 品牌规范（可选）
            context_hints: 额外上下文提示（可选）
            model: 使用的模型
            template_preset: 模板预设名称（可选）

        Returns:
            Dict: 结构化的PPT大纲
        """
        if template_preset:
            logger.info(f"使用模板预设: {template_preset}")
        logger.info("开始两阶段大纲生成...")

        # ===== 阶段1：文档分析 =====
        logger.info("阶段1: 文档分析...")
        doc_analysis = self.document_analyzer.analyze_document(
            reference_text,
            context_hints=context_hints,
            model=model
        )
        logger.info(f"文档分析完成: 类型={doc_analysis.get('document_type')}, "
                   f"主题={doc_analysis.get('main_theme')}")

        # ===== 阶段2：基于分析生成大纲 =====
        logger.info("阶段2: 基于分析生成大纲...")
        system_prompt = self._get_two_stage_system_prompt(template_preset)
        user_prompt = self._build_two_stage_user_prompt(
            doc_analysis,
            style_requirements,
            audience_profile,
            brand_guidelines,
            template_preset
        )

        result = self.llm_client.generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            expected_structure="json",
            model=model,
            max_tokens=8000
        )

        # 验证并修复结果
        result = self._validate_and_fix_result(result, reference_text, style_requirements)

        # 后处理
        result = self._post_process(result)

        # 附加分析结果
        result["_document_analysis"] = doc_analysis

        logger.info(f"两阶段大纲生成完成: {len(result.get('slides', []))} 页")
        return result

    def _get_two_stage_system_prompt(self, template_preset: str = None) -> str:
        """获取两阶段生成的系统提示"""
        base_prompt = """你是一位PPT设计架构师，正在根据预分析的文档结构设计PPT大纲。

【你的优势】
你已经收到了文档的深度分析结果，包括：
- 文档类型和核心主题
- 关键章节及其重要性评分
- 数据点和可视化建议
- 叙事结构推荐
- 目标受众推断

【设计原则 - Problem → Solution → Result】

1. 开场（30%页面）
   - 吸引注意力的标题页
   - 清晰的目录/路线图
   - 问题/背景设定

2. 核心内容（50%页面）
   - 按重要性排序的关键章节
   - 数据支撑页面
   - 案例/证据页面

3. 收尾（20%页面）
   - 解决方案总结
   - 行动号召
   - 联系方式/下一步

【页面分配策略】
- 根据 key_sections 的 importance 分数分配页面
- importance >= 8: 2-3 页
- importance 5-7: 1-2 页
- importance < 5: 合并或省略

【输出要求】
返回纯 JSON 格式，结构与标准大纲相同。
确保每个 slide 包含：
- slide_number, slide_type, title
- content_summary, key_points[]
- layout_positions{}, visual_elements{}
- emotional_tone, template_suggestion"""

        # 如果指定了模板预设，添加约束
        template_presets = get_template_presets()
        if template_preset and template_preset in template_presets:
            preset = template_presets[template_preset]
            preset_constraint = f"""

【模板预设约束 - {preset.get('name', template_preset)}】
你必须严格按照以下模板序列生成大纲：
页面类型序列: {preset.get('sequence', [])}
总页数: {preset.get('suggested_slides', 5)} 页
叙事结构: {preset.get('narrative', 'problem_solution_result')}

重要：
- 每一页的 slide_type 必须严格对应序列中的类型
- 不要增加或减少页面数量
- 根据序列中的模板类型调整内容组织"""
            return base_prompt + preset_constraint

        return base_prompt

    def _build_two_stage_user_prompt(
        self,
        doc_analysis: Dict,
        style_requirements: str,
        audience_profile: Dict = None,
        brand_guidelines: Dict = None,
        template_preset: str = None
    ) -> str:
        """构建两阶段生成的用户提示"""
        prompt_parts = [
            "【文档分析结果】",
            f"文档类型: {doc_analysis.get('document_type', '通用')}",
            f"核心主题: {doc_analysis.get('main_theme', '')}",
            f"复杂度: {doc_analysis.get('complexity_level', 'medium')}",
            f"推荐叙事结构: {doc_analysis.get('suggested_narrative', 'problem_solution_result')}",
            f"建议总页数: {doc_analysis.get('suggested_total_slides', 8)}",
            "",
            "【关键章节】"
        ]

        for section in doc_analysis.get("key_sections", []):
            prompt_parts.append(
                f"- {section.get('title', '未命名')} "
                f"(重要性: {section.get('importance', 5)}/10, "
                f"建议页数: {section.get('suggested_slides', 1)})"
            )
            prompt_parts.append(f"  摘要: {section.get('content_summary', '')[:100]}")

        if doc_analysis.get("data_points"):
            prompt_parts.extend(["", "【数据点】"])
            for dp in doc_analysis.get("data_points", [])[:5]:
                prompt_parts.append(
                    f"- {dp.get('value', '')}: {dp.get('context', '')} "
                    f"(可视化: {dp.get('visualization', '图表')})"
                )

        if doc_analysis.get("key_message"):
            prompt_parts.extend([
                "",
                f"【核心记忆点】",
                doc_analysis.get("key_message", "")
            ])

        prompt_parts.extend([
            "",
            "【风格要求】",
            style_requirements or "专业简洁"
        ])

        if audience_profile:
            prompt_parts.extend([
                "",
                "【目标受众】",
                f"类型: {audience_profile.get('type', '通用')}",
                f"专业水平: {audience_profile.get('expertise', '中等')}",
                f"关注点: {audience_profile.get('interests', '综合信息')}"
            ])
        elif doc_analysis.get("target_audience"):
            prompt_parts.extend([
                "",
                f"【推断的目标受众】",
                doc_analysis.get("target_audience", "通用受众")
            ])

        if brand_guidelines:
            prompt_parts.extend([
                "",
                "【品牌规范】",
                f"主色: {brand_guidelines.get('primary_color', '#1e3c72')}",
                f"辅色: {brand_guidelines.get('secondary_color', '#2196F3')}",
                f"风格: {brand_guidelines.get('style', '专业')}"
            ])

        # 如果有模板预设，添加约束提示
        template_presets = get_template_presets()
        if template_preset and template_preset in template_presets:
            preset = template_presets[template_preset]
            prompt_parts.extend([
                "",
                f"【模板预设】使用「{preset.get('name', template_preset)}」预设",
                f"页面序列: {' → '.join(preset.get('sequence', []))}",
                f"总页数: {preset.get('suggested_slides', 5)} 页",
                "请严格按照此模板序列生成大纲，每页的 slide_type 必须对应序列中的类型。"
            ])

        prompt_parts.extend([
            "",
            "请基于以上分析结果，生成结构化的PPT大纲。",
            "返回 JSON 格式，包含 title, subtitle, total_slides, style_theme, slides[]。"
        ])

        return "\n".join(prompt_parts)

    def _get_system_prompt(self, template_preset: str = None) -> str:
        """获取系统提示"""
        base_prompt = """你是一位资深PPT设计师，拥有10年演示设计经验。

【核心能力】
1. 信息架构：金字塔原理，先总后分，层次分明
2. 视觉叙事：用画面讲故事，而非堆砌文字
3. 情感设计：通过色彩和布局传递情感

【设计原则】
1. 一页一主题：每页只传达一个核心信息
2. 30-50-20法则：30%开场 + 50%核心 + 20%总结
3. 7±2法则：每页信息控制在7±2个单元内
4. 视觉层次：主视觉40% + 支撑30% + 留白30%

【页面类型】
- 标题页：震撼开场，3秒抓住注意力
- 目录页：清晰路线图，降低认知负荷
- 内容页：图文结合，数据可视化
- 过渡页：承上启下，保持节奏
- 总结页：强化记忆，号召行动

【输出要求】
返回纯JSON格式，不要任何额外说明文字。
必须包含：title, subtitle, total_slides, style_theme, slides[]
每个slide必须包含：slide_number, slide_type, title, content_summary, key_points[], layout_positions{}, visual_elements{}, emotional_tone"""

        # 如果指定了模板预设，添加约束
        template_presets = get_template_presets()
        if template_preset and template_preset in template_presets:
            preset = template_presets[template_preset]
            preset_constraint = f"""

【模板预设约束 - {preset.get('name', template_preset)}】
你必须严格按照以下模板序列生成大纲：
页面类型序列: {preset.get('sequence', [])}
总页数: {preset.get('suggested_slides', 5)} 页

重要：
- 每一页的 slide_type 必须严格对应序列中的类型
- 不要增加或减少页面数量
- 根据序列中的模板类型调整内容组织"""
            return base_prompt + preset_constraint

        return base_prompt

    def _build_user_prompt(self, reference_text: str, style_requirements: str, template_preset: str = None) -> str:
        """构建用户提示"""
        base_prompt = f"""【参考内容】
{reference_text}

【风格要求】
{style_requirements}

【布局说明】(16:9比例，9宫格)
- 位置：top-left/center/right, middle-left/center/right, bottom-left/center/right
- 标题通常在 top-center 或 top-left
- 主内容在 middle-center 或 middle-left
- 页码在 bottom-right
"""

        # 如果有模板预设，添加约束
        template_presets = get_template_presets()
        if template_preset and template_preset in template_presets:
            preset = template_presets[template_preset]
            base_prompt += f"""
【模板预设】使用「{preset.get('name', template_preset)}」预设
页面序列: {' → '.join(preset.get('sequence', []))}
总页数: {preset.get('suggested_slides', 5)} 页
请严格按照此模板序列生成大纲，每页的 slide_type 必须对应序列中的类型。
"""

        base_prompt += """
请生成PPT大纲，返回如下JSON格式：
{
    "title": "演示标题",
    "subtitle": "副标题",
    "total_slides": 8,
    "style_theme": "风格主题",
    "slides": [
        {
            "slide_number": 1,
            "slide_type": "标题页",
            "title": "标题",
            "content_summary": "概述",
            "key_points": ["要点1", "要点2"],
            "layout_positions": {
                "title": {"position": "middle-center", "size": "large"},
                "subtitle": {"position": "middle-center", "size": "medium"}
            },
            "visual_elements": {
                "main_visual": "背景描述",
                "supporting_graphics": "装饰元素"
            },
            "emotional_tone": "专业、吸引人"
        }
    ]
}"""
        return base_prompt

    def _validate_and_fix_result(self, result, reference_text: str, style_requirements: str) -> Dict:
        """验证并修复结果"""
        # 如果不是字典，尝试解析
        if not isinstance(result, dict):
            logger.warning(f"LLM返回的不是字典: {type(result)}")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    logger.error("无法解析LLM返回的字符串为JSON")
                    return self._get_default_outline(reference_text, style_requirements)

        # 检查错误响应
        if 'error' in result:
            logger.error(f"JSON解析失败: {result.get('error')}")
            if 'raw_response' in result:
                result = self._try_extract_json(result['raw_response'])
                if result is None:
                    return self._get_default_outline(reference_text, style_requirements)
            else:
                return self._get_default_outline(reference_text, style_requirements)

        # 确保有slides字段
        if 'slides' not in result:
            logger.warning("大纲中缺少'slides'字段")
            return self._get_default_outline(reference_text, style_requirements)

        return result

    def _try_extract_json(self, raw: str) -> Dict:
        """尝试从原始响应中提取JSON"""
        try:
            # 清理markdown代码块
            if '```json' in raw:
                start = raw.find('```json') + 7
                end = raw.rfind('```')
                if end > start:
                    raw = raw[start:end].strip()
            elif '```' in raw:
                start = raw.find('```') + 3
                end = raw.rfind('```')
                if end > start:
                    raw = raw[start:end].strip()

            # 查找JSON部分
            start_idx = raw.find('{')
            end_idx = raw.rfind('}') + 1
            if start_idx != -1 and end_idx > 0:
                json_str = raw[start_idx:end_idx]
                result = json.loads(json_str)
                logger.info("成功从原始响应中恢复JSON")
                return result
        except Exception as e:
            logger.error(f"无法从原始响应恢复JSON: {e}")

        return None

    def _post_process(self, outline: Dict) -> Dict:
        """后处理大纲"""
        # 添加页面关系推断
        if "slide_relations" not in outline:
            outline["slide_relations"] = self._infer_slide_relations(outline.get("slides", []))

        # 添加模板推荐
        for slide in outline.get("slides", []):
            if "template_suggestion" not in slide:
                slide["template_suggestion"] = self._suggest_template(slide)

        # 添加演示流程建议
        if "presentation_flow" not in outline:
            outline["presentation_flow"] = self._generate_flow_suggestions(outline)

        # 添加设计系统默认值
        if "design_system" not in outline:
            outline["design_system"] = self._get_default_design_system()

        return outline

    def _infer_slide_relations(self, slides: List[Dict]) -> List[Dict]:
        """推断页面间的关系"""
        relations = []

        for i in range(len(slides) - 1):
            current = slides[i]
            next_slide = slides[i + 1]

            current_type = current.get("slide_type", "").lower()
            next_type = next_slide.get("slide_type", "").lower()

            if "标题" in current_type and "目录" in next_type:
                relation_type = "introduction_to_overview"
            elif "问题" in current.get("title", "").lower() and "解决" in next_slide.get("title", "").lower():
                relation_type = "problem_to_solution"
            elif "数据" in current_type or "数据" in next_type:
                relation_type = "data_support"
            else:
                relation_type = "sequential"

            relations.append({
                "from_slide": i + 1,
                "to_slide": i + 2,
                "relation_type": relation_type
            })

        return relations

    def _suggest_template(self, slide: Dict) -> str:
        """根据页面内容推荐模板"""
        slide_type = slide.get("slide_type", "").lower()
        title = slide.get("title", "").lower()

        if "标题" in slide_type:
            return "hero_title"
        elif "对比" in title or "vs" in title or "对照" in title:
            return "two_column_comparison"
        elif "时间" in title or "历程" in title or "发展" in title:
            return "timeline"
        elif "数据" in slide_type or "统计" in title:
            return "data_dashboard"
        elif "案例" in slide_type or "案例" in title:
            return "case_study"
        else:
            return "standard_content"

    def _generate_flow_suggestions(self, outline: Dict) -> Dict:
        """生成演示流程建议"""
        total_slides = len(outline.get("slides", []))
        standard_path = list(range(1, total_slides + 1))

        quick_path = [1]
        for i, slide in enumerate(outline.get("slides", [])[1:], 2):
            slide_type = slide.get("slide_type", "").lower()
            if any(key in slide_type for key in ["总结", "目录", "核心"]) or i == total_slides:
                quick_path.append(i)

        if len(quick_path) < 5 and total_slides > 5:
            step = total_slides // 5
            quick_path = list(range(1, total_slides + 1, step))
            if total_slides not in quick_path:
                quick_path.append(total_slides)

        return {
            "standard_path": standard_path,
            "quick_path": sorted(list(set(quick_path))),
            "detailed_path": "all_slides_with_appendix"
        }

    def _init_slide_templates(self) -> Dict:
        """初始化页面模板库"""
        return {
            "hero_title": {
                "name": "英雄标题页",
                "layout": "中心布局，大标题",
                "best_for": "开场页、章节页"
            },
            "two_column_comparison": {
                "name": "双栏对比",
                "layout": "左右均分",
                "best_for": "对比分析、优劣势"
            },
            "timeline": {
                "name": "时间轴",
                "layout": "横向时间线",
                "best_for": "历程、计划、流程"
            },
            "data_dashboard": {
                "name": "数据仪表盘",
                "layout": "网格化数据展示",
                "best_for": "数据汇总、KPI展示"
            },
            "case_study": {
                "name": "案例研究",
                "layout": "图文混排",
                "best_for": "具体案例、成功故事"
            }
        }

    def _get_default_design_system(self) -> Dict:
        """获取默认设计系统"""
        return {
            "color_palette": {
                "primary": "#1e3c72",
                "secondary": "#2196F3",
                "accent": "#FF9800",
                "background": "#FFFFFF",
                "text": {
                    "primary": "#333333",
                    "secondary": "#666666",
                    "inverse": "#FFFFFF"
                }
            },
            "typography": {
                "heading_font": "Microsoft YaHei, sans-serif",
                "body_font": "PingFang SC, Arial, sans-serif",
                "font_sizes": {
                    "h1": "72px",
                    "h2": "48px",
                    "h3": "36px",
                    "body": "24px",
                    "small": "18px"
                }
            },
            "spacing": {
                "unit": "8px",
                "page_margin": "40px",
                "element_gap": "24px"
            }
        }

    def _get_default_outline(self, reference_text: str, style_requirements: str) -> Dict:
        """获取默认大纲结构"""
        return {
            "title": "演示文稿",
            "subtitle": "自动生成的演示文稿",
            "total_slides": 3,
            "target_audience": "通用受众",
            "presentation_goal": "信息传达",
            "style_theme": style_requirements or "专业简洁",
            "design_system": self._get_default_design_system(),
            "slides": [
                {
                    "slide_number": 1,
                    "slide_id": "title_slide",
                    "slide_type": "标题页",
                    "template_suggestion": "hero_title",
                    "title": "标题页",
                    "subtitle": "副标题",
                    "content_summary": "开场介绍",
                    "key_points": ["主题介绍"],
                    "visual_elements": {
                        "main_visual": "渐变背景",
                        "supporting_graphics": "装饰元素"
                    },
                    "speaker_notes": "开场白",
                    "emotional_tone": "专业、吸引人",
                    "background_image": "科技感渐变背景"
                },
                {
                    "slide_number": 2,
                    "slide_id": "content_1",
                    "slide_type": "内容页",
                    "template_suggestion": "standard_content",
                    "title": "主要内容",
                    "content_summary": reference_text[:200] + "..." if len(reference_text) > 200 else reference_text,
                    "key_points": ["要点1", "要点2"],
                    "visual_elements": {
                        "main_visual": "简洁背景",
                        "supporting_graphics": "图标"
                    },
                    "speaker_notes": "详细说明",
                    "emotional_tone": "清晰、专业",
                    "background_image": "简洁商务背景"
                },
                {
                    "slide_number": 3,
                    "slide_id": "summary",
                    "slide_type": "总结页",
                    "template_suggestion": "standard_content",
                    "title": "总结",
                    "content_summary": "核心要点回顾",
                    "key_points": ["总结要点"],
                    "visual_elements": {
                        "main_visual": "总结背景",
                        "supporting_graphics": "图表"
                    },
                    "speaker_notes": "总结陈述",
                    "emotional_tone": "总结性、有力",
                    "background_image": "专业总结背景"
                }
            ]
        }
