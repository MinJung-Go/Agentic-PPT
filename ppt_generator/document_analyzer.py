"""
文档分析器 - 借鉴 NotebookLM 的 Source-Grounded 理念

第一阶段：深度理解文档结构，为大纲生成提供高质量输入。
"""

import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """
    文档分析器 - 第一阶段：理解文档结构

    借鉴 NotebookLM 的核心理念：
    1. Source-Grounded：只基于用户提供的内容分析
    2. 深度结构解析：提取隐含的金字塔结构
    3. 叙事建议：推荐最佳的呈现方式
    """

    def __init__(self, llm_client):
        """
        初始化文档分析器

        Args:
            llm_client: LLM 客户端实例
        """
        self.llm_client = llm_client

    def analyze_document(
        self,
        reference_text: str,
        context_hints: Dict = None,
        model: str = "gpt-4"
    ) -> Dict:
        """
        深度分析文档，提取结构化信息

        Args:
            reference_text: 参考文档文本
            context_hints: 额外的上下文提示（可选）
            model: 使用的模型

        Returns:
            Dict: 文档分析结果
                - document_type: 文档类型
                - main_theme: 核心主题
                - key_sections: 关键章节列表
                - data_points: 数据点列表
                - entities: 关键实体
                - emotional_arc: 情感走向
                - suggested_narrative: 叙事结构建议
                - target_audience: 推断的目标受众
                - complexity_level: 复杂度等级
        """
        system_prompt = self._get_analysis_system_prompt()
        user_prompt = self._build_analysis_user_prompt(reference_text, context_hints)

        try:
            result = self.llm_client.generate_structured_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                expected_structure="json",
                model=model,
                max_tokens=4000
            )

            # 验证和补充结果
            result = self._validate_and_enhance(result, reference_text)

            logger.info(f"文档分析完成: 类型={result.get('document_type')}, "
                       f"主题={result.get('main_theme')}, "
                       f"章节数={len(result.get('key_sections', []))}")

            return result

        except Exception as e:
            logger.error(f"文档分析失败: {e}")
            return self._get_fallback_analysis(reference_text)

    def _get_analysis_system_prompt(self) -> str:
        """获取分析系统提示"""
        return """你是专业的文档分析专家，擅长从复杂文档中提取结构化信息。

【核心原则：Source-Grounded】
- 只基于用户提供的内容进行分析
- 不添加文档中没有的信息
- 对不确定的内容标注"推断"
- 保持客观中立的分析视角

【分析维度】

1. 文档类型识别
   - 商业类：商业计划、市场分析、产品介绍、公司介绍
   - 技术类：技术方案、架构设计、API文档、研发报告
   - 学术类：研究论文、学术演讲、课程内容、研究报告
   - 创意类：创意提案、设计方案、营销策划、品牌故事

2. 金字塔结构解析
   - 识别核心论点（最上层）
   - 提取支撑论据（中间层）
   - 发现具体细节（底层）

3. 信息密度评估
   - 高密度信息需要拆分展示
   - 低密度信息可以合并呈现

4. 叙事结构建议
   - Problem → Solution → Result（问题-解决-成果）
   - Chronological（时间顺序）
   - Comparison（对比分析）
   - Story-driven（故事驱动）

5. 受众推断
   - 技术受众：强调细节和逻辑
   - 商务受众：强调价值和ROI
   - 通用受众：平衡信息密度

【输出要求】
返回纯 JSON 格式，结构如下：
{
    "document_type": "文档类型",
    "main_theme": "核心主题（一句话概括）",
    "key_sections": [
        {
            "title": "章节标题",
            "content_summary": "内容摘要",
            "importance": 1-10,
            "suggested_slides": 1-3
        }
    ],
    "data_points": [
        {
            "value": "数据值",
            "context": "数据含义",
            "visualization": "建议的可视化方式"
        }
    ],
    "entities": ["关键实体1", "关键实体2"],
    "emotional_arc": "情感走向描述",
    "suggested_narrative": "推荐的叙事结构",
    "target_audience": "推断的目标受众",
    "complexity_level": "simple/medium/complex",
    "key_message": "一句话记忆点"
}"""

    def _build_analysis_user_prompt(
        self,
        reference_text: str,
        context_hints: Dict = None
    ) -> str:
        """构建分析用户提示"""
        prompt_parts = [
            "请深度分析以下文档，提取结构化信息：",
            "",
            "【文档内容】",
            reference_text,
            ""
        ]

        if context_hints:
            prompt_parts.extend([
                "【额外上下文】"
            ])
            if context_hints.get("purpose"):
                prompt_parts.append(f"- 演示目的：{context_hints['purpose']}")
            if context_hints.get("audience"):
                prompt_parts.append(f"- 目标受众：{context_hints['audience']}")
            if context_hints.get("duration"):
                prompt_parts.append(f"- 演示时长：{context_hints['duration']}分钟")
            prompt_parts.append("")

        prompt_parts.extend([
            "请返回 JSON 格式的分析结果，包含：",
            "1. document_type - 文档类型",
            "2. main_theme - 核心主题",
            "3. key_sections - 关键章节（含重要性评分和建议页数）",
            "4. data_points - 数据点（含可视化建议）",
            "5. entities - 关键实体",
            "6. emotional_arc - 情感走向",
            "7. suggested_narrative - 叙事结构建议",
            "8. target_audience - 目标受众推断",
            "9. complexity_level - 复杂度",
            "10. key_message - 核心记忆点"
        ])

        return "\n".join(prompt_parts)

    def _validate_and_enhance(self, result: Dict, reference_text: str) -> Dict:
        """验证并增强分析结果"""
        # 确保必要字段存在
        defaults = {
            "document_type": "通用文档",
            "main_theme": self._extract_main_theme(reference_text),
            "key_sections": [],
            "data_points": [],
            "entities": [],
            "emotional_arc": "neutral",
            "suggested_narrative": "problem_solution_result",
            "target_audience": "通用受众",
            "complexity_level": "medium",
            "key_message": ""
        }

        for key, default_value in defaults.items():
            if key not in result or not result[key]:
                result[key] = default_value

        # 确保 key_sections 有内容
        if not result["key_sections"]:
            result["key_sections"] = self._auto_extract_sections(reference_text)

        # 计算建议的总页数
        total_slides = sum(
            section.get("suggested_slides", 1)
            for section in result["key_sections"]
        )
        result["suggested_total_slides"] = min(max(total_slides + 2, 5), 15)  # 加上标题和总结页

        return result

    def _extract_main_theme(self, text: str) -> str:
        """从文本中提取主题（简单实现）"""
        # 取前100个字符作为主题提示
        clean_text = text.strip()[:100]
        if len(clean_text) < len(text.strip()):
            clean_text += "..."
        return clean_text

    def _auto_extract_sections(self, text: str) -> List[Dict]:
        """自动提取章节（简单实现）"""
        sections = []
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for i, para in enumerate(paragraphs[:5]):  # 最多5个章节
            sections.append({
                "title": f"章节 {i + 1}",
                "content_summary": para[:100] + "..." if len(para) > 100 else para,
                "importance": 5,
                "suggested_slides": 1
            })

        return sections

    def _get_fallback_analysis(self, reference_text: str) -> Dict:
        """获取降级分析结果"""
        return {
            "document_type": "通用文档",
            "main_theme": self._extract_main_theme(reference_text),
            "key_sections": self._auto_extract_sections(reference_text),
            "data_points": [],
            "entities": [],
            "emotional_arc": "neutral",
            "suggested_narrative": "problem_solution_result",
            "target_audience": "通用受众",
            "complexity_level": "medium",
            "key_message": "",
            "suggested_total_slides": 8
        }

    def extract_brand_elements(self, text: str) -> Dict:
        """
        从文本中提取品牌元素

        Args:
            text: 文档文本

        Returns:
            Dict: 品牌元素
                - company_name: 公司名称
                - product_names: 产品名称列表
                - brand_keywords: 品牌关键词
        """
        # 简单实现：后续可以用 NER 增强
        return {
            "company_name": None,
            "product_names": [],
            "brand_keywords": []
        }

    def estimate_presentation_duration(self, analysis: Dict) -> Dict:
        """
        估算演示时长

        Args:
            analysis: 文档分析结果

        Returns:
            Dict: 时长估算
                - total_minutes: 总时长（分钟）
                - per_slide_seconds: 每页平均秒数
                - time_allocation: 时间分配建议
        """
        total_slides = analysis.get("suggested_total_slides", 8)
        complexity = analysis.get("complexity_level", "medium")

        # 根据复杂度调整每页时间
        seconds_per_slide = {
            "simple": 45,
            "medium": 60,
            "complex": 90
        }.get(complexity, 60)

        total_seconds = total_slides * seconds_per_slide
        total_minutes = total_seconds / 60

        # 30-50-20 时间分配
        return {
            "total_minutes": round(total_minutes, 1),
            "per_slide_seconds": seconds_per_slide,
            "time_allocation": {
                "opening": f"{round(total_minutes * 0.3, 1)} 分钟",
                "main_content": f"{round(total_minutes * 0.5, 1)} 分钟",
                "closing": f"{round(total_minutes * 0.2, 1)} 分钟"
            }
        }
