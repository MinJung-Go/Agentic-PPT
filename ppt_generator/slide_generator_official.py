"""
PPT幻灯片生成器 - 官方 Google Gemini API 版本

使用 Google 官方 genai SDK 调用 Nano Banana Pro (gemini-3-pro-image-preview) 生成图片
"""

import asyncio
import base64
import uuid
import os
import json
from typing import Dict, Optional, Any
import logging
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# 尝试导入官方 SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai SDK 未安装，请运行: pip install google-genai")


class ImageGenerationConfig:
    """图片生成配置"""
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    DEFAULT_MODEL = "gemini-3-pro-image-preview"  # Nano Banana Pro
    FALLBACK_MODEL = "gemini-2.5-flash-image"     # Nano Banana


class ImageGenerationParams(BaseModel):
    """图片生成参数 - 与 slide_generator.py 保持一致"""
    prompt: str = Field(description="**English Image Prompt**")
    ratio: str = Field(
        description="图片比例",
        default="16:9",
    )
    output_dir: str = Field(description="输出目录", default="output/images")
    context_variables: Dict = Field(default_factory=dict, description="Context variables", exclude=True)


class ImageGenerationTool:
    """
    图片生成工具 - 使用 Google 官方 genai SDK

    支持两个模型:
    - gemini-3-pro-image-preview (Nano Banana Pro) - 高质量，支持 4K
    - gemini-2.5-flash-image (Nano Banana) - 快速，性价比高
    """

    def __init__(self, api_key: str = None, model: str = None):
        """
        初始化图片生成工具

        Args:
            api_key: Google API Key，如果不提供则从环境变量 GEMINI_API_KEY 获取
            model: 模型名称，默认使用 Nano Banana Pro
        """
        if not GENAI_AVAILABLE:
            raise ImportError("请先安装 google-genai: pip install google-genai")

        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 GEMINI_API_KEY 环境变量或传入 api_key 参数")

        self.model = model or ImageGenerationConfig.DEFAULT_MODEL
        self.client = genai.Client(api_key=self.api_key)

        logger.info(f"ImageGenerationTool 初始化完成，使用模型: {self.model}")

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        image_size: str = "2K",
        output_dir: str = "output/images",
        key_prefix: str = "ppt_slide"
    ) -> Dict[str, Any]:
        """
        生成图片

        Args:
            prompt: 图片描述提示词（建议使用英文）
            aspect_ratio: 宽高比，如 "16:9", "1:1", "4:3" 等
            image_size: 分辨率，"1K", "2K", "4K"（仅 Pro 模型支持）
            output_dir: 输出目录
            key_prefix: 文件名前缀

        Returns:
            Dict: 包含 success, file_path, filename, error 等信息
        """
        last_error = None

        for attempt in range(ImageGenerationConfig.MAX_RETRIES + 1):
            try:
                if attempt > 0:
                    logger.info(f"重试 {attempt}/{ImageGenerationConfig.MAX_RETRIES}...")
                    await asyncio.sleep(ImageGenerationConfig.RETRY_DELAY * (1.5 ** (attempt - 1)))

                # 构建配置
                image_config = types.ImageConfig(aspect_ratio=aspect_ratio)

                # Nano Banana Pro 支持 image_size 参数
                if "pro" in self.model.lower() and image_size:
                    image_config = types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=image_size
                    )

                # 调用 API
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=['IMAGE'],
                        image_config=image_config
                    )
                )

                # 解析响应
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # 获取图片数据
                        image_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type or "image/png"

                        # 保存图片
                        save_result = await self._save_image(
                            image_data, mime_type, output_dir, key_prefix
                        )

                        if save_result:
                            return {
                                "success": True,
                                "file_path": save_result['file_path'],
                                "filename": save_result['filename'],
                                "mime_type": save_result['mime_type'],
                                "size": save_result['size'],
                                "prompt_used": prompt,
                                "model": self.model,
                                "aspect_ratio": aspect_ratio
                            }

                    # 尝试使用 as_image() 方法
                    elif hasattr(part, 'as_image'):
                        try:
                            image = part.as_image()
                            if image:
                                save_result = await self._save_pil_image(
                                    image, output_dir, key_prefix
                                )
                                if save_result:
                                    return {
                                        "success": True,
                                        "file_path": save_result['file_path'],
                                        "filename": save_result['filename'],
                                        "mime_type": "image/png",
                                        "size": save_result['size'],
                                        "prompt_used": prompt,
                                        "model": self.model,
                                        "aspect_ratio": aspect_ratio
                                    }
                        except Exception as e:
                            logger.warning(f"as_image() 方法失败: {e}")

                last_error = "响应中未找到图片数据"
                logger.warning(f"尝试 {attempt + 1}: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"尝试 {attempt + 1} 失败: {last_error}")

                # 如果是内容策略违规，不再重试
                if "policy" in last_error.lower() or "safety" in last_error.lower():
                    break

        return {"success": False, "error": f"生成失败: {last_error}"}

    async def _save_image(
        self,
        image_data: bytes,
        mime_type: str,
        output_dir: str,
        key_prefix: str
    ) -> Optional[Dict]:
        """保存图片数据到本地"""
        try:
            os.makedirs(output_dir, exist_ok=True)

            # 如果是 base64 编码的字符串，先解码
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            ext = 'png' if 'png' in mime_type else 'jpg'
            filename = f"{key_prefix}_{timestamp}_{unique_id}.{ext}"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            logger.info(f"图片已保存: {filepath}")

            return {
                "file_path": filepath,
                "filename": filename,
                "mime_type": mime_type,
                "size": len(image_bytes)
            }

        except Exception as e:
            logger.error(f"保存图片失败: {e}")
            return None

    async def _save_pil_image(
        self,
        image,
        output_dir: str,
        key_prefix: str
    ) -> Optional[Dict]:
        """保存 PIL Image 对象到本地"""
        try:
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            filename = f"{key_prefix}_{timestamp}_{unique_id}.png"
            filepath = os.path.join(output_dir, filename)

            image.save(filepath)
            file_size = os.path.getsize(filepath)

            logger.info(f"图片已保存: {filepath}")

            return {
                "file_path": filepath,
                "filename": filename,
                "mime_type": "image/png",
                "size": file_size
            }

        except Exception as e:
            logger.error(f"保存 PIL 图片失败: {e}")
            return None

    async def gemini_generate(self, params: ImageGenerationParams) -> Dict[str, Any]:
        """
        使用 Gemini API 生成图片 - 与 slide_generator.py 接口保持一致

        Args:
            params: ImageGenerationParams 参数对象

        Returns:
            Dict: 生成结果
        """
        result = await self.generate_image(
            prompt=params.prompt,
            aspect_ratio=params.ratio,
            output_dir=params.output_dir,
            key_prefix="ppt_bg"
        )

        # 如果成功，将结果存入 context_variables（与原版一致）
        if result.get("success") and params.context_variables is not None:
            image_key = f"image_{uuid.uuid4().hex[:8]}"
            params.context_variables[image_key] = {
                "file_path": result['file_path'],
                "filename": result['filename'],
                "rephraser_result": params.prompt,
                "aspect_ratio": params.ratio,
                "mime_type": result.get('mime_type', 'image/png'),
                "file_size": result.get('size', 0)
            }

        return result

    async def __call__(self, params: ImageGenerationParams) -> Dict[str, Any]:
        """
        执行图片生成 - 与 slide_generator.py 接口保持一致

        Args:
            params: ImageGenerationParams 参数对象

        Returns:
            Dict: 生成结果
        """
        logger.info(f"Starting image generation with prompt: {params.prompt[:100]}...")

        try:
            result = await self.gemini_generate(params)

            if result.get("success"):
                logger.info(f"Successfully generated image: {result.get('file_path')}")
            else:
                logger.error(f"Gemini generation failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Exception in gemini_generate: {e}")
            return {"success": False, "error": f"Image generation failed: {str(e)}"}


class SlideGenerator:
    """
    PPT幻灯片生成器 - 使用官方 Google Gemini API

    生成完整的 PPT 页面图片
    """

    def __init__(self, image_generator: ImageGenerationTool):
        """
        初始化幻灯片生成器 - 与 slide_generator.py 接口保持一致

        Args:
            image_generator: ImageGenerationTool 实例
        """
        self.image_generator = image_generator
        self.template_styles = self._init_template_styles()
        self.quality_presets = self._init_quality_presets()
        self.style_presets = self._init_style_presets()

    async def generate_slide_as_image(self, slide_info: Dict, slide_index: int,
                                       outline_result: dict, style_requirements: str,
                                       output_dir: str, style_hints: dict = None) -> Dict:
        """
        生成整页PPT图片（包含标题、内容、布局等）- 与 slide_generator.py 接口保持一致

        Args:
            slide_info: 当前幻灯片信息
            slide_index: 幻灯片索引（从0开始）
            outline_result: 完整的大纲结果字典
            style_requirements: 风格要求
            output_dir: 输出目录
            style_hints: 模板预设的风格提示（可选）

        Returns:
            Dict: 生成结果，包含 success, file_path, filename 等
        """
        slide_id = slide_info.get('slide_id', f'slide_{slide_index + 1}')
        total_slides = len(outline_result.get('slides', []))
        logger.info(f"正在为 {slide_id} (第 {slide_index + 1}/{total_slides} 页) 生成 PPT 图片...")

        try:
            prompt_dict = self._build_slide_image_prompt(
                slide_info, slide_index, outline_result, style_requirements, style_hints
            )
            clean_dict = self._simplify_prompt_dict(prompt_dict)

            system_prompt = f"""Create a professional PPT slide image.

LAYOUT (where to place elements):
- layout_positions: element positions on 16:9 slide
  - "top-left/center/right": header area
  - "middle-left/center/right": main content area
  - "bottom-left/center/right": footer area

PRIORITY:
1. layout_positions → Place elements at specified positions
2. title → Main headline at its position
3. style → Follow design style
4. colors → Use for elements
5. key_points → Show as icons/short text

CHINESE TEXT RENDERING (CRITICAL):
- All Chinese text MUST be crisp, clear, highly legible
- Use modern sans-serif Chinese font (like Noto Sans SC, PingFang)
- Bold weight for titles, medium for body text
- High contrast between text and background
- Proper character spacing, line height 1.5-1.8x
- NO blurry, distorted, or pixelated Chinese characters
- Anti-aliasing must be smooth

PAGE NUMBER (MUST BE IDENTICAL ON ALL SLIDES):
- Position: bottom-right corner, exactly 12px from edges
- Format: {slide_index + 1}/{total_slides}
- Style: small (10pt), gray (#666666), 75% opacity
- CRITICAL: EXACT same position, size, color on EVERY slide

RULES:
- Clean, professional background
- Minimal text, large visuals
- 16:9 ratio
- Consistent visual style

DATA:
{json.dumps(clean_dict, ensure_ascii=False, separators=(',', ':'))}"""

            params = ImageGenerationParams(
                prompt=system_prompt,
                ratio="16:9",
                output_dir=os.path.join(output_dir, "images")
            )

            result = await self.image_generator(params)

            if result.get("success"):
                slide_info['generated_slide_image'] = {
                    'file_path': result['file_path'],
                    'filename': result['filename'],
                    'mime_type': result.get('mime_type', 'image/png'),
                    'prompt_used': prompt_dict
                }
                return result
            else:
                return {"success": False, "error": result.get('error', 'Unknown error')}

        except Exception as e:
            logger.error(f"第 {slide_index + 1} 页 PPT 图片生成出错: {str(e)}")
            return {"success": False, "error": str(e)}

    def _build_slide_image_prompt(self, slide_info: Dict, slide_index: int,
                                   outline_result: dict, style_requirements: str,
                                   style_hints: dict = None) -> Dict:
        """构建生成整页PPT图片的结构化提示词 - 与 slide_generator.py 保持一致"""
        total_slides = len(outline_result.get('slides', []))

        prompt_dict = {
            "page": f"{slide_index + 1}/{total_slides}",
            "slide_type": self._get_slide_type_description(slide_info.get('slide_type', '内容页')),
            "title": slide_info.get('title', ''),
            "key_points": slide_info.get('key_points', [])[:3],
            "layout_positions": self._extract_layout_positions(slide_info.get('layout_positions', {})),
            "style": style_requirements or outline_result.get('style_theme', ''),
            "colors": self._extract_color_scheme(outline_result)
        }

        # 如果有模板预设的 style_hints，添加到提示词中
        if style_hints:
            # 添加风格提示作为优先级更高的样式指导
            style_hint_parts = []
            if style_hints.get('background'):
                style_hint_parts.append(f"Background: {style_hints['background']}")
            if style_hints.get('typography'):
                style_hint_parts.append(f"Typography: {style_hints['typography']}")
            if style_hints.get('layout'):
                style_hint_parts.append(f"Layout: {style_hints['layout']}")
            if style_hints.get('visual'):
                style_hint_parts.append(f"Visual: {style_hints['visual']}")
            if style_hints.get('special'):
                style_hint_parts.append(f"Special: {style_hints['special']}")

            if style_hint_parts:
                prompt_dict["preset_style"] = ". ".join(style_hint_parts)

            # 如果 style_hints 有颜色定义，优先使用
            if style_hints.get('colors'):
                prompt_dict["colors"] = {
                    "palette": style_hints['colors']
                }

        return prompt_dict

    def _extract_layout_positions(self, layout_positions: Dict) -> Dict:
        """提取并简化布局位置信息"""
        if not layout_positions:
            return {}

        simplified = {}
        for element, info in layout_positions.items():
            if isinstance(info, dict):
                pos = info.get('position', '')
                size = info.get('size', '')
                desc = info.get('description', '')

                if pos:
                    simplified[element] = pos
                    if size:
                        simplified[element] += f" ({size})"
                    if desc and len(desc) < 20:
                        simplified[element] += f": {desc}"

        return simplified

    def _extract_color_scheme(self, outline_result: dict) -> Dict:
        """提取颜色方案"""
        design_system = outline_result.get('design_system', {})
        color_palette = design_system.get('color_palette', {})
        return {
            "primary": color_palette.get('primary', ''),
            "secondary": color_palette.get('secondary', ''),
            "accent": color_palette.get('accent', ''),
            "background": color_palette.get('background', '')
        }

    def _simplify_prompt_dict(self, prompt_dict: Dict, max_str_len: int = 80, max_points: int = 3) -> Dict:
        """精简提示词字典，移除空值，截断过长内容"""
        clean = {}

        for key, value in prompt_dict.items():
            if value is None or value == '' or value == [] or value == {}:
                continue

            if isinstance(value, str):
                if len(value) > max_str_len:
                    clean[key] = value[:max_str_len] + '...'
                else:
                    clean[key] = value

            elif isinstance(value, list):
                simplified_list = []
                for item in value[:max_points]:
                    if isinstance(item, str) and len(item) > 30:
                        simplified_list.append(item[:30] + '...')
                    else:
                        simplified_list.append(item)
                if simplified_list:
                    clean[key] = simplified_list

            elif isinstance(value, dict):
                if key == 'layout_positions':
                    if value:
                        clean[key] = value
                elif key == 'colors':
                    clean_colors = {k: v for k, v in value.items() if v}
                    if clean_colors:
                        clean[key] = clean_colors
                else:
                    clean_sub = {k: v for k, v in value.items() if v}
                    if clean_sub:
                        clean[key] = clean_sub
            else:
                clean[key] = value

        return clean

    def _get_slide_type_description(self, slide_type: str) -> str:
        """获取页面类型的英文描述"""
        type_map = {
            '标题': "Title slide with large centered headline, impactful and professional",
            '目录': "Table of contents slide with structured list and clear hierarchy",
            '过渡': "Section divider slide with minimal design",
            '总结': "Conclusion slide summarizing key takeaways",
            '致谢': "Thank you slide with contact information",
            '内容': "Content slide with clear layout and visual elements"
        }

        for key, desc in type_map.items():
            if key in slide_type:
                return desc
        return "Content slide with clear layout and visual elements"

    def _init_template_styles(self) -> Dict[str, Dict]:
        """初始化模板风格映射"""
        return {
            'hero_title': {
                'style': 'grand opening slide, impactful hero section, powerful centered composition',
                'mood': 'inspiring, professional, attention-grabbing, prestigious',
                'visual': 'sophisticated gradient background, subtle particle effects, depth layers, premium feel',
                'details': 'large negative space for title, subtle motion blur, cinematic lighting'
            },
            'two_column_comparison': {
                'style': 'balanced dual layout, symmetrical composition, clear visual separation',
                'mood': 'analytical, objective, comparative, structured',
                'visual': 'split screen background, subtle vertical divider, contrasting but harmonious sides',
                'details': 'left-right balance, complementary color zones, clear boundaries'
            },
            'timeline': {
                'style': 'horizontal flow design, chronological progression, linear journey',
                'mood': 'progressive, evolutionary, forward-moving, dynamic',
                'visual': 'flowing lines, gradient progression, time-based visual metaphor, path visualization',
                'details': 'left to right movement, milestone markers, continuous flow'
            },
            'data_dashboard': {
                'style': 'structured grid layout, information architecture, data-centric design',
                'mood': 'precise, analytical, trustworthy, technical',
                'visual': 'subtle grid patterns, clean geometric background, data visualization backdrop',
                'details': 'mathematical precision, chart-friendly colors, neutral tones'
            },
            'case_study': {
                'style': 'storytelling layout, narrative composition, contextual design',
                'mood': 'engaging, realistic, relatable, practical',
                'visual': 'contextual imagery, real-world backdrop, scenario-based background',
                'details': 'photographic elements, environmental context, authentic feel'
            },
            'standard_content': {
                'style': 'versatile layout, flexible composition, universal design',
                'mood': 'professional, clear, focused, adaptable',
                'visual': 'clean gradient background, subtle texture overlay, understated elegance',
                'details': 'maximum readability, content-first approach, minimal distractions'
            }
        }

    def _init_quality_presets(self) -> Dict[str, list]:
        """初始化质量提升的预设词汇"""
        return {
            'base_quality': [
                'ultra high quality',
                '4K resolution',
                'professional photography',
                'perfectly composed',
                'crystal clear'
            ],
            'lighting': [
                'perfect lighting',
                'studio lighting',
                'soft ambient light',
                'golden hour lighting',
                'professional illumination'
            ],
            'composition': [
                'rule of thirds',
                'perfect composition',
                'balanced layout',
                'harmonious arrangement',
                'aesthetically pleasing'
            ],
            'render_quality': [
                'photorealistic',
                'hyperdetailed',
                'sharp focus',
                'high definition',
                'premium quality'
            ],
            'negative_prompts': [
                'no text',
                'no watermarks',
                'no logos',
                'no people',
                'no faces',
                'clean background',
                'uncluttered'
            ]
        }

    def _init_style_presets(self) -> Dict[str, Dict]:
        """初始化风格预设"""
        return {
            'corporate': {
                'keywords': ['corporate', 'business', 'professional', 'executive'],
                'colors': ['navy blue', 'steel gray', 'white', 'subtle gold accents'],
                'elements': ['abstract geometric shapes', 'clean lines', 'minimal design'],
                'atmosphere': 'sophisticated, trustworthy, established'
            },
            'tech': {
                'keywords': ['technology', 'digital', 'futuristic', 'innovative'],
                'colors': ['electric blue', 'neon purple', 'dark background', 'glowing accents'],
                'elements': ['circuit patterns', 'data streams', 'holographic effects', 'grid patterns'],
                'atmosphere': 'cutting-edge, dynamic, forward-thinking'
            },
            'creative': {
                'keywords': ['creative', 'artistic', 'vibrant', 'imaginative'],
                'colors': ['vibrant gradients', 'rainbow spectrum', 'bold contrasts'],
                'elements': ['fluid shapes', 'organic forms', 'artistic brushstrokes'],
                'atmosphere': 'inspiring, energetic, unconventional'
            },
            'minimal': {
                'keywords': ['minimalist', 'simple', 'clean', 'zen'],
                'colors': ['monochrome', 'soft pastels', 'white space', 'muted tones'],
                'elements': ['negative space', 'simple geometry', 'subtle textures'],
                'atmosphere': 'calm, focused, elegant'
            },
            'nature': {
                'keywords': ['natural', 'organic', 'environmental', 'sustainable'],
                'colors': ['forest green', 'earth tones', 'sky blue', 'natural wood'],
                'elements': ['leaves', 'water', 'mountains', 'natural textures'],
                'atmosphere': 'refreshing, authentic, grounded'
            }
        }


# 便捷函数
async def generate_slide_image(
    prompt: str,
    api_key: str = None,
    aspect_ratio: str = "16:9",
    output_dir: str = "output/images"
) -> Dict:
    """
    便捷函数：快速生成一张 PPT 幻灯片图片

    Args:
        prompt: 图片描述
        api_key: Google API Key（可选，默认从环境变量获取）
        aspect_ratio: 宽高比
        output_dir: 输出目录

    Returns:
        Dict: 生成结果

    Example:
        >>> result = await generate_slide_image(
        ...     "Create a professional title slide about AI Technology",
        ...     aspect_ratio="16:9"
        ... )
        >>> print(result['file_path'])
    """
    generator = ImageGenerationTool(api_key=api_key)
    return await generator.generate_image(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        output_dir=output_dir
    )


# 测试代码
if __name__ == "__main__":
    async def test():
        """测试官方 API"""
        print("=" * 50)
        print("测试 Google Gemini 官方 API 图片生成")
        print("=" * 50)

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("错误: 请设置 GEMINI_API_KEY 环境变量")
            return

        generator = ImageGenerationTool(api_key=api_key)

        prompt = """Create a professional PPT title slide.

TITLE: AI Technology Overview
STYLE: Modern tech style, deep blue gradient background, clean typography

Requirements:
- 16:9 aspect ratio
- Large centered title in white
- Subtle tech-themed decorative elements
- Professional and sleek design
"""

        print(f"提示词:\n{prompt[:200]}...")
        print("-" * 50)

        result = await generator.generate_image(
            prompt=prompt,
            aspect_ratio="16:9",
            output_dir="test_output"
        )

        if result.get("success"):
            print(f"✅ 生成成功!")
            print(f"   文件: {result['file_path']}")
            print(f"   大小: {result['size']} bytes")
        else:
            print(f"❌ 生成失败: {result.get('error')}")

    asyncio.run(test())
