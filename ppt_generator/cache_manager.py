"""
缓存管理器 - PPT 生成缓存

主要功能：
1. 大纲缓存 - 避免重复生成相同内容的大纲
2. 图片缓存 - 缓存已生成的幻灯片图片
3. 增量更新 - 只重新生成变化的页面
4. 自动清理 - 定期清理过期缓存
"""

import hashlib
import json
import os
import shutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheManager:
    """PPT 生成缓存管理器"""

    def __init__(
        self,
        cache_dir: str = ".cache/ppt_generator",
        cache_ttl_days: int = 7
    ):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
            cache_ttl_days: 缓存有效期（天）
        """
        self.cache_dir = Path(cache_dir)
        self.outline_cache_dir = self.cache_dir / "outlines"
        self.image_cache_dir = self.cache_dir / "images"
        self.metadata_file = self.cache_dir / "metadata.json"
        self.cache_ttl = timedelta(days=cache_ttl_days)

        # 创建缓存目录
        self._ensure_cache_dirs()

        # 加载元数据
        self.metadata = self._load_metadata()

    def _ensure_cache_dirs(self):
        """确保缓存目录存在"""
        self.outline_cache_dir.mkdir(parents=True, exist_ok=True)
        self.image_cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self) -> Dict:
        """加载缓存元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存元数据失败: {e}")
        return {"version": "1.0", "entries": {}}

    def _save_metadata(self):
        """保存缓存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存元数据失败: {e}")

    def _compute_hash(self, *args) -> str:
        """计算缓存键哈希"""
        combined = "||".join(str(arg) for arg in args)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    # ==================== 大纲缓存 ====================

    def get_cached_outline(
        self,
        reference_text: str,
        style_requirements: str,
        model: str
    ) -> Optional[Dict]:
        """
        获取缓存的大纲

        Args:
            reference_text: 参考文本
            style_requirements: 风格要求
            model: 使用的模型

        Returns:
            Optional[Dict]: 缓存的大纲，如果不存在或已过期则返回 None
        """
        cache_key = self._compute_hash(reference_text, style_requirements, model)
        cache_file = self.outline_cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            logger.debug(f"大纲缓存未命中: {cache_key}")
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)

            # 检查是否过期
            cached_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
            if datetime.now() - cached_time > self.cache_ttl:
                logger.info(f"大纲缓存已过期: {cache_key}")
                cache_file.unlink()  # 删除过期缓存
                return None

            logger.info(f"大纲缓存命中: {cache_key}")
            return cached.get('outline')

        except Exception as e:
            logger.warning(f"读取大纲缓存失败: {e}")
            return None

    def cache_outline(
        self,
        reference_text: str,
        style_requirements: str,
        model: str,
        outline: Dict
    ):
        """
        缓存大纲

        Args:
            reference_text: 参考文本
            style_requirements: 风格要求
            model: 使用的模型
            outline: 生成的大纲
        """
        cache_key = self._compute_hash(reference_text, style_requirements, model)
        cache_file = self.outline_cache_dir / f"{cache_key}.json"

        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'model': model,
            'text_hash': self._compute_hash(reference_text),
            'style_hash': self._compute_hash(style_requirements),
            'outline': outline
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            # 更新元数据
            self.metadata["entries"][cache_key] = {
                "type": "outline",
                "created_at": cache_data['cached_at'],
                "file": str(cache_file)
            }
            self._save_metadata()

            logger.info(f"大纲已缓存: {cache_key}")

        except Exception as e:
            logger.error(f"缓存大纲失败: {e}")

    # ==================== 图片缓存 ====================

    def get_cached_image(self, prompt_hash: str) -> Optional[str]:
        """
        获取缓存的图片路径

        Args:
            prompt_hash: 提示词哈希

        Returns:
            Optional[str]: 缓存图片的路径，如果不存在则返回 None
        """
        # 查找匹配的缓存图片
        for filename in os.listdir(self.image_cache_dir):
            if filename.startswith(prompt_hash):
                cache_path = self.image_cache_dir / filename

                # 检查是否过期
                mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
                if datetime.now() - mtime > self.cache_ttl:
                    logger.info(f"图片缓存已过期: {filename}")
                    cache_path.unlink()
                    return None

                logger.info(f"图片缓存命中: {filename}")
                return str(cache_path)

        return None

    def cache_image(self, prompt: str, image_path: str) -> str:
        """
        缓存图片

        Args:
            prompt: 生成图片的提示词
            image_path: 原始图片路径

        Returns:
            str: 缓存后的图片路径
        """
        prompt_hash = self._compute_hash(prompt)
        ext = os.path.splitext(image_path)[1]
        cache_filename = f"{prompt_hash}{ext}"
        cache_path = self.image_cache_dir / cache_filename

        try:
            shutil.copy2(image_path, cache_path)

            # 更新元数据
            self.metadata["entries"][prompt_hash] = {
                "type": "image",
                "created_at": datetime.now().isoformat(),
                "file": str(cache_path)
            }
            self._save_metadata()

            logger.info(f"图片已缓存: {cache_filename}")
            return str(cache_path)

        except Exception as e:
            logger.error(f"缓存图片失败: {e}")
            return image_path

    def get_image_prompt_hash(self, prompt: str) -> str:
        """获取图片提示词的哈希值"""
        return self._compute_hash(prompt)

    # ==================== 增量更新 ====================

    def get_changed_slides(
        self,
        old_outline: Dict,
        new_outline: Dict
    ) -> List[int]:
        """
        比较新旧大纲，返回需要重新生成的页面索引

        Args:
            old_outline: 旧大纲
            new_outline: 新大纲

        Returns:
            List[int]: 需要重新生成的页面索引列表
        """
        changed_indices = []

        old_slides = old_outline.get('slides', [])
        new_slides = new_outline.get('slides', [])

        for i, new_slide in enumerate(new_slides):
            if i >= len(old_slides):
                # 新增页面
                changed_indices.append(i)
                continue

            old_slide = old_slides[i]

            # 比较关键字段
            if self._slide_changed(old_slide, new_slide):
                changed_indices.append(i)

        logger.info(f"检测到 {len(changed_indices)} 个页面需要重新生成")
        return changed_indices

    def _slide_changed(self, old_slide: Dict, new_slide: Dict) -> bool:
        """检查幻灯片是否发生变化"""
        # 比较关键字段
        key_fields = ['title', 'slide_type', 'key_points', 'content_summary']

        for field in key_fields:
            old_value = old_slide.get(field)
            new_value = new_slide.get(field)

            if old_value != new_value:
                return True

        return False

    def get_cached_slides_for_outline(
        self,
        outline: Dict
    ) -> Dict[int, str]:
        """
        获取大纲对应的已缓存幻灯片图片

        Args:
            outline: 大纲

        Returns:
            Dict[int, str]: 页面索引 -> 缓存图片路径的映射
        """
        cached_slides = {}

        for i, slide in enumerate(outline.get('slides', [])):
            # 构建该页面的缓存键
            slide_key = self._compute_hash(
                slide.get('title', ''),
                slide.get('slide_type', ''),
                str(slide.get('key_points', []))
            )

            cached_path = self.get_cached_image(slide_key)
            if cached_path:
                cached_slides[i] = cached_path

        return cached_slides

    # ==================== 缓存清理 ====================

    def cleanup_expired(self) -> Dict[str, int]:
        """
        清理过期缓存

        Returns:
            Dict: 清理统计信息
        """
        stats = {
            "outlines_removed": 0,
            "images_removed": 0,
            "bytes_freed": 0
        }

        now = datetime.now()

        # 清理大纲缓存
        for cache_file in self.outline_cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)

                cached_time = datetime.fromisoformat(cached.get('cached_at', '2000-01-01'))
                if now - cached_time > self.cache_ttl:
                    size = cache_file.stat().st_size
                    cache_file.unlink()
                    stats["outlines_removed"] += 1
                    stats["bytes_freed"] += size

            except Exception as e:
                logger.warning(f"清理大纲缓存失败: {cache_file}, {e}")

        # 清理图片缓存
        for cache_file in self.image_cache_dir.iterdir():
            try:
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if now - mtime > self.cache_ttl:
                    size = cache_file.stat().st_size
                    cache_file.unlink()
                    stats["images_removed"] += 1
                    stats["bytes_freed"] += size

            except Exception as e:
                logger.warning(f"清理图片缓存失败: {cache_file}, {e}")

        logger.info(f"缓存清理完成: 删除 {stats['outlines_removed']} 个大纲, "
                   f"{stats['images_removed']} 张图片, "
                   f"释放 {stats['bytes_freed'] / 1024:.2f} KB")

        return stats

    def clear_all(self):
        """清空所有缓存"""
        try:
            # 删除所有缓存文件
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)

            # 重新创建目录
            self._ensure_cache_dirs()

            # 重置元数据
            self.metadata = {"version": "1.0", "entries": {}}
            self._save_metadata()

            logger.info("所有缓存已清空")

        except Exception as e:
            logger.error(f"清空缓存失败: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict: 缓存统计
        """
        outline_count = len(list(self.outline_cache_dir.glob("*.json")))
        image_count = len(list(self.image_cache_dir.iterdir()))

        outline_size = sum(f.stat().st_size for f in self.outline_cache_dir.glob("*.json"))
        image_size = sum(f.stat().st_size for f in self.image_cache_dir.iterdir())

        return {
            "outline_count": outline_count,
            "image_count": image_count,
            "outline_size_kb": outline_size / 1024,
            "image_size_mb": image_size / (1024 * 1024),
            "total_size_mb": (outline_size + image_size) / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
            "ttl_days": self.cache_ttl.days
        }
