"""
智能错误处理器 - 处理图片生成过程中的各类错误

主要功能：
1. 内容策略违规处理 - 自动替换敏感词
2. 超时处理 - 简化 prompt 重试
3. API 错误处理 - 指数退避重试
4. 降级方案 - 生成纯文字/简单背景的幻灯片
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """错误类型枚举"""
    CONTENT_POLICY = "content_policy"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """恢复动作枚举"""
    MODIFY_PROMPT = "modify_prompt"
    SIMPLIFY_PROMPT = "simplify_prompt"
    RETRY_WITH_DELAY = "retry_with_delay"
    USE_FALLBACK = "use_fallback"
    ABORT = "abort"


@dataclass
class ErrorAnalysis:
    """错误分析结果"""
    error_type: ErrorType
    severity: str  # "low", "medium", "high", "critical"
    recovery_action: RecoveryAction
    modified_prompt: Optional[str]
    retry_delay: float
    max_retries: int
    should_retry: bool
    fallback_data: Optional[Dict]
    message: str


class SmartErrorHandler:
    """智能错误处理器"""

    # 内容策略敏感词及其替代词
    SENSITIVE_WORDS = {
        # 暴力相关
        "暴力": "和平",
        "战争": "合作",
        "武器": "工具",
        "攻击": "互动",
        "战斗": "竞争",
        "杀": "解决",
        "死亡": "变化",
        "血": "能量",

        # 政治敏感
        "政治": "社会",
        "政府": "组织",
        "革命": "变革",
        "抗议": "表达",

        # 成人内容
        "性感": "优雅",
        "裸露": "自然",
        "色情": "艺术",

        # 其他敏感
        "毒品": "物质",
        "赌博": "娱乐",
        "欺诈": "营销"
    }

    # 英文敏感词
    SENSITIVE_WORDS_EN = {
        "violence": "peace",
        "war": "cooperation",
        "weapon": "tool",
        "attack": "interact",
        "kill": "resolve",
        "death": "change",
        "blood": "energy",
        "nude": "natural",
        "sexy": "elegant",
        "drug": "substance",
        "gambling": "entertainment"
    }

    # 内容策略违规的回退提示词
    CONTENT_POLICY_FALLBACKS = {
        "violence": {
            "modifier": "peaceful, harmonious, collaborative atmosphere",
            "background": "soft gradient background with abstract shapes"
        },
        "adult": {
            "modifier": "professional business environment, corporate setting",
            "background": "clean minimalist background"
        },
        "political": {
            "modifier": "neutral, objective, balanced presentation",
            "background": "subtle geometric pattern background"
        },
        "default": {
            "modifier": "abstract geometric shapes, clean minimal design",
            "background": "simple gradient or solid color background"
        }
    }

    def __init__(self):
        """初始化错误处理器"""
        self.error_history: List[Dict] = []

    def analyze_error(
        self,
        error_response: Dict,
        original_prompt: str,
        attempt: int = 0
    ) -> ErrorAnalysis:
        """
        分析错误并生成恢复策略

        Args:
            error_response: API 返回的错误响应
            original_prompt: 原始提示词
            attempt: 当前尝试次数

        Returns:
            ErrorAnalysis: 错误分析结果
        """
        error_code = error_response.get("code", -1)
        error_message = str(error_response.get("message", "")).lower()
        error_type = self._classify_error(error_code, error_message)

        # 记录错误历史
        self.error_history.append({
            "type": error_type.value,
            "code": error_code,
            "message": error_message,
            "attempt": attempt
        })

        # 根据错误类型生成恢复策略
        if error_type == ErrorType.CONTENT_POLICY:
            return self._handle_content_policy_error(original_prompt, attempt)

        elif error_type == ErrorType.TIMEOUT:
            return self._handle_timeout_error(original_prompt, attempt)

        elif error_type == ErrorType.RATE_LIMIT:
            return self._handle_rate_limit_error(original_prompt, attempt)

        elif error_type == ErrorType.API_ERROR:
            return self._handle_api_error(original_prompt, attempt, error_message)

        elif error_type == ErrorType.NETWORK_ERROR:
            return self._handle_network_error(original_prompt, attempt)

        else:
            return self._handle_unknown_error(original_prompt, attempt)

    def _classify_error(self, error_code: int, error_message: str) -> ErrorType:
        """分类错误类型"""
        # Gemini API 错误码
        if error_code == 5:
            return ErrorType.CONTENT_POLICY

        # 超时关键词
        if any(kw in error_message for kw in ["timeout", "timed out", "超时"]):
            return ErrorType.TIMEOUT

        # 速率限制
        if any(kw in error_message for kw in ["rate limit", "too many requests", "429", "限流"]):
            return ErrorType.RATE_LIMIT

        # 网络错误
        if any(kw in error_message for kw in ["connection", "network", "dns", "网络"]):
            return ErrorType.NETWORK_ERROR

        # API 错误（4xx, 5xx）
        if 400 <= error_code < 600:
            return ErrorType.API_ERROR

        return ErrorType.UNKNOWN

    def _handle_content_policy_error(
        self,
        original_prompt: str,
        attempt: int
    ) -> ErrorAnalysis:
        """处理内容策略违规错误"""
        # 检测违规类型
        violation_type = self._detect_violation_type(original_prompt)
        fallback = self.CONTENT_POLICY_FALLBACKS.get(
            violation_type,
            self.CONTENT_POLICY_FALLBACKS["default"]
        )

        if attempt == 0:
            # 第一次：尝试替换敏感词
            modified_prompt = self._sanitize_prompt(original_prompt)
            return ErrorAnalysis(
                error_type=ErrorType.CONTENT_POLICY,
                severity="high",
                recovery_action=RecoveryAction.MODIFY_PROMPT,
                modified_prompt=modified_prompt,
                retry_delay=0.5,
                max_retries=2,
                should_retry=True,
                fallback_data=None,
                message="检测到内容策略违规，已替换敏感词"
            )

        elif attempt == 1:
            # 第二次：使用抽象化描述
            abstract_prompt = self._create_abstract_prompt(original_prompt, fallback)
            return ErrorAnalysis(
                error_type=ErrorType.CONTENT_POLICY,
                severity="high",
                recovery_action=RecoveryAction.SIMPLIFY_PROMPT,
                modified_prompt=abstract_prompt,
                retry_delay=1.0,
                max_retries=2,
                should_retry=True,
                fallback_data=None,
                message="使用抽象化描述重试"
            )

        else:
            # 第三次及以后：使用降级方案
            return ErrorAnalysis(
                error_type=ErrorType.CONTENT_POLICY,
                severity="critical",
                recovery_action=RecoveryAction.USE_FALLBACK,
                modified_prompt=None,
                retry_delay=0,
                max_retries=0,
                should_retry=False,
                fallback_data={"type": "gradient_fallback", "style": fallback["background"]},
                message="内容策略违规无法恢复，使用降级方案"
            )

    def _handle_timeout_error(
        self,
        original_prompt: str,
        attempt: int
    ) -> ErrorAnalysis:
        """处理超时错误"""
        if attempt < 3:
            # 简化 prompt 并重试
            simplified = self._simplify_prompt(original_prompt)
            delay = 2.0 * (attempt + 1)  # 递增延迟

            return ErrorAnalysis(
                error_type=ErrorType.TIMEOUT,
                severity="medium",
                recovery_action=RecoveryAction.SIMPLIFY_PROMPT,
                modified_prompt=simplified,
                retry_delay=delay,
                max_retries=3,
                should_retry=True,
                fallback_data=None,
                message=f"请求超时，简化 prompt 后 {delay}s 后重试"
            )
        else:
            return ErrorAnalysis(
                error_type=ErrorType.TIMEOUT,
                severity="high",
                recovery_action=RecoveryAction.USE_FALLBACK,
                modified_prompt=None,
                retry_delay=0,
                max_retries=0,
                should_retry=False,
                fallback_data={"type": "simple_fallback"},
                message="多次超时，使用降级方案"
            )

    def _handle_rate_limit_error(
        self,
        original_prompt: str,
        attempt: int
    ) -> ErrorAnalysis:
        """处理速率限制错误"""
        # 指数退避
        delay = min(2 ** (attempt + 1), 60)  # 最大60秒

        if attempt < 5:
            return ErrorAnalysis(
                error_type=ErrorType.RATE_LIMIT,
                severity="medium",
                recovery_action=RecoveryAction.RETRY_WITH_DELAY,
                modified_prompt=original_prompt,  # 保持原 prompt
                retry_delay=delay,
                max_retries=5,
                should_retry=True,
                fallback_data=None,
                message=f"触发速率限制，{delay}s 后重试"
            )
        else:
            return ErrorAnalysis(
                error_type=ErrorType.RATE_LIMIT,
                severity="high",
                recovery_action=RecoveryAction.USE_FALLBACK,
                modified_prompt=None,
                retry_delay=0,
                max_retries=0,
                should_retry=False,
                fallback_data={"type": "simple_fallback"},
                message="速率限制未解除，使用降级方案"
            )

    def _handle_api_error(
        self,
        original_prompt: str,
        attempt: int,
        error_message: str
    ) -> ErrorAnalysis:
        """处理 API 错误"""
        if attempt < 2:
            return ErrorAnalysis(
                error_type=ErrorType.API_ERROR,
                severity="medium",
                recovery_action=RecoveryAction.RETRY_WITH_DELAY,
                modified_prompt=original_prompt,
                retry_delay=3.0,
                max_retries=2,
                should_retry=True,
                fallback_data=None,
                message=f"API 错误: {error_message[:50]}，稍后重试"
            )
        else:
            return ErrorAnalysis(
                error_type=ErrorType.API_ERROR,
                severity="high",
                recovery_action=RecoveryAction.USE_FALLBACK,
                modified_prompt=None,
                retry_delay=0,
                max_retries=0,
                should_retry=False,
                fallback_data={"type": "error_fallback", "error": error_message},
                message="API 错误持续，使用降级方案"
            )

    def _handle_network_error(
        self,
        original_prompt: str,
        attempt: int
    ) -> ErrorAnalysis:
        """处理网络错误"""
        if attempt < 3:
            delay = 5.0 * (attempt + 1)
            return ErrorAnalysis(
                error_type=ErrorType.NETWORK_ERROR,
                severity="medium",
                recovery_action=RecoveryAction.RETRY_WITH_DELAY,
                modified_prompt=original_prompt,
                retry_delay=delay,
                max_retries=3,
                should_retry=True,
                fallback_data=None,
                message=f"网络错误，{delay}s 后重试"
            )
        else:
            return ErrorAnalysis(
                error_type=ErrorType.NETWORK_ERROR,
                severity="critical",
                recovery_action=RecoveryAction.ABORT,
                modified_prompt=None,
                retry_delay=0,
                max_retries=0,
                should_retry=False,
                fallback_data={"type": "network_error"},
                message="网络持续异常，中止生成"
            )

    def _handle_unknown_error(
        self,
        original_prompt: str,
        attempt: int
    ) -> ErrorAnalysis:
        """处理未知错误"""
        if attempt < 2:
            return ErrorAnalysis(
                error_type=ErrorType.UNKNOWN,
                severity="medium",
                recovery_action=RecoveryAction.RETRY_WITH_DELAY,
                modified_prompt=original_prompt,
                retry_delay=2.0,
                max_retries=2,
                should_retry=True,
                fallback_data=None,
                message="未知错误，尝试重试"
            )
        else:
            return ErrorAnalysis(
                error_type=ErrorType.UNKNOWN,
                severity="high",
                recovery_action=RecoveryAction.USE_FALLBACK,
                modified_prompt=None,
                retry_delay=0,
                max_retries=0,
                should_retry=False,
                fallback_data={"type": "unknown_error"},
                message="未知错误持续，使用降级方案"
            )

    def _detect_violation_type(self, prompt: str) -> str:
        """检测内容策略违规类型"""
        prompt_lower = prompt.lower()

        violence_keywords = ["暴力", "战争", "武器", "攻击", "violence", "war", "weapon"]
        adult_keywords = ["性感", "裸露", "色情", "sexy", "nude", "adult"]
        political_keywords = ["政治", "政府", "革命", "political", "government"]

        if any(kw in prompt_lower for kw in violence_keywords):
            return "violence"
        elif any(kw in prompt_lower for kw in adult_keywords):
            return "adult"
        elif any(kw in prompt_lower for kw in political_keywords):
            return "political"

        return "default"

    def _sanitize_prompt(self, prompt: str) -> str:
        """清理敏感词"""
        result = prompt

        # 替换中文敏感词
        for sensitive, safe in self.SENSITIVE_WORDS.items():
            result = result.replace(sensitive, safe)

        # 替换英文敏感词（不区分大小写）
        for sensitive, safe in self.SENSITIVE_WORDS_EN.items():
            pattern = re.compile(re.escape(sensitive), re.IGNORECASE)
            result = pattern.sub(safe, result)

        return result

    def _create_abstract_prompt(self, original_prompt: str, fallback: Dict) -> str:
        """创建抽象化的 prompt"""
        # 提取核心信息（标题等）
        lines = original_prompt.split("\n")
        title_line = ""
        for line in lines:
            if "title" in line.lower() or "标题" in line:
                title_line = line
                break

        abstract = f"""Create a professional PPT slide image.

Style: {fallback['modifier']}
Background: {fallback['background']}

Requirements:
- Clean, minimal design
- Professional appearance
- 16:9 aspect ratio
- No text rendering issues

{title_line}
"""
        return abstract

    def _simplify_prompt(self, prompt: str) -> str:
        """简化 prompt"""
        # 移除详细描述，保留核心指令
        lines = prompt.split("\n")
        simplified_lines = []

        important_keywords = ["title", "标题", "slide", "ppt", "style", "风格", "color", "颜色"]

        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in important_keywords):
                simplified_lines.append(line)
            elif len(line.strip()) < 50:  # 保留短行
                simplified_lines.append(line)

        # 限制总长度
        simplified = "\n".join(simplified_lines)
        if len(simplified) > 500:
            simplified = simplified[:500] + "..."

        return simplified

    def create_fallback_slide(self, slide_info: Dict, fallback_type: str = "gradient") -> Dict:
        """
        创建降级版幻灯片

        Args:
            slide_info: 原始幻灯片信息
            fallback_type: 降级类型

        Returns:
            Dict: 降级幻灯片数据
        """
        return {
            "type": "fallback",
            "fallback_type": fallback_type,
            "title": slide_info.get("title", ""),
            "key_points": slide_info.get("key_points", [])[:3],
            "background": {
                "type": "gradient",
                "colors": ["#1e3c72", "#2a5298"]
            },
            "text_color": "#FFFFFF",
            "message": "此页面使用降级方案生成"
        }

    def get_error_summary(self) -> Dict:
        """获取错误统计摘要"""
        if not self.error_history:
            return {"total_errors": 0}

        error_counts = {}
        for error in self.error_history:
            error_type = error["type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        return {
            "total_errors": len(self.error_history),
            "error_counts": error_counts,
            "last_error": self.error_history[-1] if self.error_history else None
        }

    def clear_history(self):
        """清空错误历史"""
        self.error_history.clear()
