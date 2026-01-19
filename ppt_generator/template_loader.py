"""
PPT 模板预设加载器 - 从 YAML 配置文件加载

支持从 configs/templates/ 目录加载自定义 PPT 模板预设。
用户可以通过添加新的 YAML 文件来创建自定义模板，无需修改代码。
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class TemplateLoader:
    """
    模板预设加载器

    从 configs/templates/ 目录加载 YAML 格式的模板预设文件。
    支持热加载和缓存机制。

    YAML 模板格式示例:
    ```yaml
    name: "模板名称"
    description: "模板描述"
    sequence:
      - title
      - content
      - conclusion_cta
    narrative: "problem_solution_result"
    suggested_slides: 5
    style_hints:  # 可选
      background: "背景描述"
      typography: "字体描述"
      colors:
        - "#000000"
        - "#FFFFFF"
      layout: "布局描述"
      visual: "视觉元素描述"
      special: "特殊要求"  # 可选
    ```
    """

    def __init__(self, config_dir: str = None):
        """
        初始化模板加载器

        Args:
            config_dir: 配置目录路径。如果为 None，则使用项目根目录下的 configs/templates
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # 默认查找项目根目录下的 configs/templates
            self.config_dir = Path(__file__).parent.parent / "configs" / "templates"

        self._cache: Dict[str, Dict] = {}
        self._loaded = False

    def load_all(self) -> Dict[str, Dict]:
        """
        加载所有模板预设

        Returns:
            Dict[str, Dict]: 模板预设字典，key 为模板名称（文件名），value 为模板配置
        """
        if self._loaded:
            return self._cache

        if not self.config_dir.exists():
            logger.warning(f"模板配置目录不存在: {self.config_dir}")
            return {}

        for yaml_file in sorted(self.config_dir.glob("*.yaml")):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    preset = yaml.safe_load(f)
                    if preset is None:
                        logger.warning(f"空的模板文件: {yaml_file}")
                        continue

                    key = yaml_file.stem  # 文件名作为 key
                    self._cache[key] = preset
                    logger.debug(f"已加载模板: {key} - {preset.get('name', '未命名')}")

            except yaml.YAMLError as e:
                logger.error(f"YAML 解析错误 {yaml_file}: {e}")
            except Exception as e:
                logger.error(f"加载模板失败 {yaml_file}: {e}")

        self._loaded = True
        logger.info(f"已加载 {len(self._cache)} 个模板预设")
        return self._cache

    def get_preset(self, name: str) -> Optional[Dict]:
        """
        获取指定名称的模板预设

        Args:
            name: 模板名称（对应 YAML 文件名，不含扩展名）

        Returns:
            模板配置字典，如果不存在则返回 None
        """
        self.load_all()
        return self._cache.get(name)

    def list_presets(self) -> List[Dict]:
        """
        列出所有可用的模板预设

        Returns:
            List[Dict]: 预设列表，每项包含 key, name, description
        """
        self.load_all()
        return [
            {
                "key": k,
                "name": v.get("name", k),
                "description": v.get("description", "")
            }
            for k, v in self._cache.items()
        ]

    def reload(self) -> Dict[str, Dict]:
        """
        重新加载所有模板（支持热更新）

        Returns:
            Dict[str, Dict]: 重新加载后的模板预设字典
        """
        self._cache.clear()
        self._loaded = False
        logger.info("正在重新加载模板预设...")
        return self.load_all()

    def add_template_dir(self, extra_dir: str) -> None:
        """
        添加额外的模板目录（用于加载用户自定义模板）

        Args:
            extra_dir: 额外的模板目录路径
        """
        extra_path = Path(extra_dir)
        if not extra_path.exists():
            logger.warning(f"额外模板目录不存在: {extra_dir}")
            return

        for yaml_file in sorted(extra_path.glob("*.yaml")):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    preset = yaml.safe_load(f)
                    if preset:
                        key = yaml_file.stem
                        self._cache[key] = preset
                        logger.info(f"已加载额外模板: {key}")
            except Exception as e:
                logger.error(f"加载额外模板失败 {yaml_file}: {e}")


# 全局单例
_loader: Optional[TemplateLoader] = None


def get_template_loader(config_dir: str = None) -> TemplateLoader:
    """
    获取模板加载器单例

    Args:
        config_dir: 配置目录路径（仅在首次调用时生效）

    Returns:
        TemplateLoader: 模板加载器实例
    """
    global _loader
    if _loader is None:
        _loader = TemplateLoader(config_dir)
    return _loader


def get_template_presets() -> Dict[str, Dict]:
    """
    获取所有模板预设

    兼容原有 TEMPLATE_PRESETS 用法，返回相同格式的字典。

    Returns:
        Dict[str, Dict]: 模板预设字典
    """
    return get_template_loader().load_all()


def reload_templates() -> Dict[str, Dict]:
    """
    重新加载所有模板

    Returns:
        Dict[str, Dict]: 重新加载后的模板预设字典
    """
    return get_template_loader().reload()
