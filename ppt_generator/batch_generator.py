"""
批量图片生成器 - 借鉴 Nano Banana Pro 的批量生成能力

主要功能：
1. 风格锚定 - 首先生成标题页作为风格锚定，后续页面参考
2. 按类型分组批量生成 - 同类型页面一起生成，保持风格一致
3. 参考图上下文 - 支持上传品牌手册等参考图
"""

import asyncio
import logging
import base64
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from .prompt_templates import PromptTemplateSystem
from .error_handler import SmartErrorHandler, ErrorAnalysis, RecoveryAction

logger = logging.getLogger(__name__)


@dataclass
class BatchGenerationResult:
    """批量生成结果"""
    slide_index: int
    success: bool
    file_path: Optional[str]
    error: Optional[str]
    from_cache: bool = False
    retries: int = 0


class BatchImageGenerator:
    """
    批量图片生成器

    借鉴 Nano Banana Pro 的能力：
    1. 风格锚定机制
    2. 批量生成
    3. 参考图上下文（最多14张）
    """

    def __init__(self, image_tool, cache_manager=None):
        """
        初始化批量生成器

        Args:
            image_tool: 图片生成工具实例
            cache_manager: 缓存管理器（可选）
        """
        self.image_tool = image_tool
        self.cache_manager = cache_manager
        self.prompt_system = PromptTemplateSystem()
        self.error_handler = SmartErrorHandler()

        # 风格锚定
        self.style_anchor: Optional[Dict] = None
        self.style_anchor_image: Optional[str] = None

    async def generate_with_style_consistency(
        self,
        slides: List[Dict],
        outline_result: Dict,
        style_requirements: str,
        output_dir: str,
        brand_references: List[str] = None,
        max_concurrent: int = 4,
        style_hints: Dict = None
    ) -> List[BatchGenerationResult]:
        """
        批量生成保持风格一致的幻灯片图片

        Args:
            slides: 幻灯片信息列表
            outline_result: 完整大纲结果
            style_requirements: 风格要求
            output_dir: 输出目录
            brand_references: 品牌参考图路径列表（最多14张）
            max_concurrent: 最大并发数
            style_hints: 模板预设的风格提示（可选）

        Returns:
            List[BatchGenerationResult]: 生成结果列表
        """
        self.style_hints = style_hints  # 保存风格提示
        total_slides = len(slides)
        logger.info(f"开始批量生成 {total_slides} 张幻灯片，并发数: {max_concurrent}")
        if style_hints:
            logger.info(f"使用风格提示: {style_hints.get('background', '')}")

        results: List[BatchGenerationResult] = []

        # ===== 步骤1：生成风格锚定图 =====
        anchor_slide = self._find_anchor_slide(slides)
        anchor_index = slides.index(anchor_slide)

        logger.info(f"生成风格锚定图（页面 {anchor_index + 1}）...")
        anchor_result = await self._generate_anchor(
            anchor_slide,
            anchor_index,
            outline_result,
            style_requirements,
            output_dir,
            brand_references
        )

        if anchor_result.success:
            self.style_anchor = self._extract_style_description(anchor_slide, style_requirements)
            self.style_anchor_image = anchor_result.file_path
            logger.info("风格锚定图生成成功")
        else:
            logger.warning("风格锚定图生成失败，继续使用独立生成模式")

        results.append(anchor_result)

        # ===== 步骤2：按类型分组批量生成剩余页面 =====
        remaining_slides = [
            (i, slide) for i, slide in enumerate(slides)
            if i != anchor_index
        ]

        # 按类型分组
        slide_groups = self._group_slides_by_type(remaining_slides)

        # 并发生成每组
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_slide_with_semaphore(
            index: int,
            slide: Dict
        ) -> BatchGenerationResult:
            async with semaphore:
                return await self._generate_single_slide(
                    slide,
                    index,
                    outline_result,
                    style_requirements,
                    output_dir,
                    brand_references
                )

        # 创建所有任务
        tasks = []
        for slide_type, group in slide_groups.items():
            logger.info(f"处理 {slide_type} 类型页面，共 {len(group)} 页")
            for index, slide in group:
                tasks.append(generate_slide_with_semaphore(index, slide))

        # 并发执行
        group_results = await asyncio.gather(*tasks)
        results.extend(group_results)

        # 按索引排序
        results.sort(key=lambda x: x.slide_index)

        # 统计
        success_count = sum(1 for r in results if r.success)
        cache_count = sum(1 for r in results if r.from_cache)
        logger.info(f"批量生成完成: {success_count}/{total_slides} 成功, "
                   f"{cache_count} 从缓存获取")

        return results

    def _find_anchor_slide(self, slides: List[Dict]) -> Dict:
        """
        找到用作风格锚定的幻灯片

        优先选择：
        1. 标题页
        2. 第一页
        """
        for slide in slides:
            slide_type = slide.get('slide_type', '').lower()
            if '标题' in slide_type or 'title' in slide_type:
                return slide

        return slides[0] if slides else {}

    async def _generate_anchor(
        self,
        slide: Dict,
        index: int,
        outline_result: Dict,
        style_requirements: str,
        output_dir: str,
        brand_references: List[str] = None
    ) -> BatchGenerationResult:
        """生成风格锚定图"""
        # 构建增强的锚定 prompt
        prompt = self._build_anchor_prompt(
            slide,
            index,
            outline_result,
            style_requirements,
            brand_references
        )

        try:
            # 优先使用内部版本，如果不存在则使用官方版本
            try:
                from .slide_generator import ImageGenerationParams
            except ImportError:
                from .slide_generator_official import ImageGenerationParams

            params = ImageGenerationParams(
                prompt=prompt,
                ratio="16:9",
                output_dir=os.path.join(output_dir, "images")
            )

            result = await self.image_tool.gemini_generate(params)

            if result.get("success"):
                return BatchGenerationResult(
                    slide_index=index,
                    success=True,
                    file_path=result.get("file_path"),
                    error=None
                )
            else:
                return BatchGenerationResult(
                    slide_index=index,
                    success=False,
                    file_path=None,
                    error=result.get("error", "Unknown error")
                )

        except Exception as e:
            logger.error(f"生成风格锚定图失败: {e}")
            return BatchGenerationResult(
                slide_index=index,
                success=False,
                file_path=None,
                error=str(e)
            )

    async def _generate_single_slide(
        self,
        slide: Dict,
        index: int,
        outline_result: Dict,
        style_requirements: str,
        output_dir: str,
        brand_references: List[str] = None
    ) -> BatchGenerationResult:
        """生成单张幻灯片"""
        total_slides = len(outline_result.get('slides', []))

        # 检查缓存
        if self.cache_manager:
            cache_key = self.cache_manager.get_image_prompt_hash(
                f"{slide.get('title')}_{slide.get('slide_type')}_{str(slide.get('key_points', []))}"
            )
            cached_path = self.cache_manager.get_cached_image(cache_key)
            if cached_path:
                return BatchGenerationResult(
                    slide_index=index,
                    success=True,
                    file_path=cached_path,
                    error=None,
                    from_cache=True
                )

        # 构建 prompt
        prompt = self._build_slide_prompt(
            slide,
            index,
            total_slides,
            style_requirements,
            brand_references
        )

        # 带错误恢复的生成
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 优先使用内部版本，如果不存在则使用官方版本
                try:
                    from .slide_generator import ImageGenerationParams
                except ImportError:
                    from .slide_generator_official import ImageGenerationParams

                params = ImageGenerationParams(
                    prompt=prompt,
                    ratio="16:9",
                    output_dir=os.path.join(output_dir, "images")
                )

                result = await self.image_tool.gemini_generate(params)

                if result.get("success"):
                    file_path = result.get("file_path")

                    # 缓存成功的图片
                    if self.cache_manager and file_path:
                        self.cache_manager.cache_image(prompt, file_path)

                    return BatchGenerationResult(
                        slide_index=index,
                        success=True,
                        file_path=file_path,
                        error=None,
                        retries=attempt
                    )

                # 错误处理
                error_analysis = self.error_handler.analyze_error(
                    result,
                    prompt,
                    attempt
                )

                if error_analysis.should_retry and error_analysis.modified_prompt:
                    prompt = error_analysis.modified_prompt
                    logger.info(f"页面 {index + 1}: {error_analysis.message}")
                    await asyncio.sleep(error_analysis.retry_delay)
                else:
                    return BatchGenerationResult(
                        slide_index=index,
                        success=False,
                        file_path=None,
                        error=error_analysis.message,
                        retries=attempt
                    )

            except Exception as e:
                logger.error(f"页面 {index + 1} 生成异常: {e}")
                if attempt == max_retries - 1:
                    return BatchGenerationResult(
                        slide_index=index,
                        success=False,
                        file_path=None,
                        error=str(e),
                        retries=attempt
                    )
                await asyncio.sleep(2)

        return BatchGenerationResult(
            slide_index=index,
            success=False,
            file_path=None,
            error="Max retries exceeded",
            retries=max_retries
        )

    def _build_anchor_prompt(
        self,
        slide: Dict,
        index: int,
        outline_result: Dict,
        style_requirements: str,
        brand_references: List[str] = None
    ) -> str:
        """构建风格锚定图的 prompt"""
        total_slides = len(outline_result.get('slides', []))

        prompt_parts = [
            "Create a hero title slide that establishes the visual style for an entire presentation.",
        ]

        # 【关键】将模板预设风格提示放在最前面，优先级最高
        style_hints = getattr(self, 'style_hints', None)
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
                "⚠️ This is the FOUNDATION style for the ENTIRE presentation!",
                "⚠️ Do NOT deviate from these visual requirements!",
                "=" * 60,
            ])

        prompt_parts.extend([
            "",
            "[ROLE] This is the STYLE ANCHOR slide - all subsequent slides will match this style.",
            "",
            f"[SLIDE INFO]",
            f"Title: {slide.get('title', 'Untitled')}",
            f"Type: {slide.get('slide_type', 'Title')}",
            f"Total Presentation: {total_slides} slides",
            "",
            f"[STYLE REQUIREMENTS]",
            f"{style_requirements}",
            "",
            "[DESIGN SPECIFICATIONS]",
            "- Establish a clear visual language",
            "- Define color palette through usage",
            "- Set typography hierarchy",
            "- Create memorable visual identity",
            "- 16:9 aspect ratio",
            "",
            "[CHINESE TEXT RENDERING - CRITICAL]",
            "- All Chinese text MUST be crisp, clear, highly legible",
            "- Use modern Chinese font (Noto Sans SC, PingFang, Microsoft YaHei style)",
            "- Bold weight for title, proper anti-aliasing",
            "- High contrast between text and background",
            "- NO blurry or distorted Chinese characters",
            "",
            "[PAGE NUMBER TEMPLATE - DEFINE FOR ALL SLIDES]",
            f"- Position: bottom-right corner, exactly 12px from edges",
            f"- Format: 1/{total_slides}",
            "- Style: small (10pt), gray (#666666), 75% opacity",
            "- This EXACT style must be used on ALL subsequent slides",
            "",
            "[QUALITY]",
            "- Professional, premium quality",
            "- Clean, modern design",
            "- High visual impact"
        ])

        if brand_references:
            prompt_parts.extend([
                "",
                "[BRAND REFERENCES]",
                f"Follow visual style from {min(len(brand_references), 14)} reference images"
            ])

        # 结尾再次强调风格
        if style_hints:
            prompt_parts.extend([
                "",
                "[FINAL REMINDER]",
                "Remember: Apply the PRESET STYLE defined at the beginning!",
                f"Key visual: {style_hints.get('visual', '')}",
                f"Key colors: {', '.join(style_hints.get('colors', []))}"
            ])

        return "\n".join(prompt_parts)

    def _build_slide_prompt(
        self,
        slide: Dict,
        index: int,
        total_slides: int,
        style_requirements: str,
        brand_references: List[str] = None
    ) -> str:
        """构建单页幻灯片的 prompt"""
        # 使用 PromptTemplateSystem 构建，传递 style_hints
        prompt = self.prompt_system.build_image_prompt(
            slide_info=slide,
            slide_index=index,
            total_slides=total_slides,
            style_requirements=style_requirements,
            style_hints=getattr(self, 'style_hints', None)
        )

        # 如果有风格锚定，添加风格一致性指令
        if self.style_anchor:
            prompt = f"""[STYLE CONSISTENCY - CRITICAL]
Match the visual style of the anchor slide EXACTLY:
{self.style_anchor.get('description', '')}

[CONSISTENT ELEMENTS - MUST MATCH ANCHOR]
1. Color palette: Use SAME colors as anchor slide
2. Typography: Use SAME font style and weights
3. Page number: EXACT same position (bottom-right, 12px from edge), size (10pt), color (#666666)
4. Layout spacing: Match margins and padding
5. Chinese text: Same crisp, clear rendering quality

---

{prompt}"""

        return prompt

    def _group_slides_by_type(
        self,
        slides: List[Tuple[int, Dict]]
    ) -> Dict[str, List[Tuple[int, Dict]]]:
        """按类型分组幻灯片"""
        groups: Dict[str, List[Tuple[int, Dict]]] = {}

        for index, slide in slides:
            slide_type = slide.get('slide_type', 'content').lower()

            # 规范化类型名
            if '标题' in slide_type or 'title' in slide_type:
                type_key = 'title'
            elif '目录' in slide_type or 'toc' in slide_type:
                type_key = 'toc'
            elif '数据' in slide_type or 'data' in slide_type:
                type_key = 'data'
            elif '时间' in slide_type or 'timeline' in slide_type:
                type_key = 'timeline'
            elif '总结' in slide_type or 'conclusion' in slide_type:
                type_key = 'conclusion'
            else:
                type_key = 'content'

            if type_key not in groups:
                groups[type_key] = []
            groups[type_key].append((index, slide))

        return groups

    def _extract_style_description(
        self,
        slide: Dict,
        style_requirements: str
    ) -> Dict:
        """从锚定页面提取风格描述"""
        style_info = {
            "description": f"Style based on: {style_requirements}",
            "slide_type": slide.get('slide_type', ''),
            "colors": slide.get('visual_elements', {}).get('colors', []),
            "mood": slide.get('emotional_tone', '')
        }

        # 保存完整的 style_hints 以便后续页面使用
        style_hints = getattr(self, 'style_hints', None)
        if style_hints:
            style_info["style_hints"] = style_hints
            # 增强描述
            style_parts = []
            if style_hints.get('background'):
                style_parts.append(f"Background: {style_hints['background']}")
            if style_hints.get('typography'):
                style_parts.append(f"Typography: {style_hints['typography']}")
            if style_hints.get('colors'):
                style_parts.append(f"Colors: {', '.join(style_hints['colors'])}")
            if style_hints.get('layout'):
                style_parts.append(f"Layout: {style_hints['layout']}")
            if style_hints.get('visual'):
                style_parts.append(f"Visual: {style_hints['visual']}")

            if style_parts:
                style_info["description"] = " | ".join(style_parts)

        return style_info

    def _encode_reference_image(self, image_path: str) -> Optional[str]:
        """编码参考图为 base64"""
        try:
            if not os.path.exists(image_path):
                return None

            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')

        except Exception as e:
            logger.warning(f"编码参考图失败: {image_path}, {e}")
            return None

    def reset_style_anchor(self):
        """重置风格锚定"""
        self.style_anchor = None
        self.style_anchor_image = None
