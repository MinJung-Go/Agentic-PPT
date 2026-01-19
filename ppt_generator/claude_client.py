"""
统一AI客户端模块 - 兼容OpenAI和Claude API格式
"""

import os
import json
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class UnifiedAIClient:
    """统一AI客户端 - 支持OpenAI和Claude API格式"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 provider: Optional[str] = None):
        """
        初始化统一AI客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量读取
            base_url: API基础URL（用于OpenAI兼容的API）
            provider: 指定提供商 ('openai', 'claude', 'auto')
        """
        self.provider = provider or 'auto'
        self.base_url = base_url
        self.api_key = api_key
        
        # 初始化客户端
        self._init_clients()
        
    def _init_clients(self):
        """初始化API客户端"""
        self.openai_client = None
        self.claude_client = None
        
        # 尝试初始化Claude客户端
        if self.provider == 'claude':
            try:
                from anthropic import Anthropic
                claude_key = self.api_key or os.getenv('ANTHROPIC_API_KEY')
                if claude_key:
                    self.claude_client = Anthropic(api_key=claude_key)
            except ImportError:
                print("Anthropic库未安装，将跳过Claude支持")
            except Exception as e:
                print(f"初始化Claude客户端失败: {e}")
        else:
            try:
                import openai
                openai_key = self.api_key or os.getenv('OPENAI_API_KEY')
                if openai_key:
                    if self.base_url:
                        self.openai_client = openai.OpenAI(
                            api_key=openai_key,
                            base_url=self.base_url
                        )
                    else:
                        self.openai_client = openai.OpenAI(api_key=openai_key)
            except ImportError:
                print("OpenAI库未安装，将跳过OpenAI支持")
            except Exception as e:
                print(f"初始化OpenAI客户端失败: {e}")
    
    def _detect_provider(self, model: str) -> str:
        """
        根据模型名称检测提供商
        
        Args:
            model: 模型名称
            
        Returns:
            str: 提供商名称
        """
        if 'claude' in model.lower():
            return 'claude'
        elif any(name in model.lower() for name in ['gpt', 'o1', 'davinci', 'curie', 'babbage', 'ada']):
            return 'openai'
        elif self.openai_client:
            return 'openai'
        elif self.claude_client:
            return 'claude'
        else:
            raise ValueError("无法检测提供商，请确保至少配置了一个API")
    
    def chat_completions_create(self,
                              model: str,
                              messages: List[Dict[str, str]],
                              temperature: float = 0.7,
                              max_tokens: Optional[int] = None,
                              stream: bool = False,
                              **kwargs) -> Dict[str, Any]:
        """
        OpenAI兼容的chat completions接口
        
        Args:
            model: 模型名称
            messages: 消息列表，格式为 [{"role": "user|assistant|system", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大令牌数
            stream: 是否流式输出
            **kwargs: 其他参数
            
        Returns:
            Dict: OpenAI格式的响应
        """
        provider = self._detect_provider(model)
        
        if provider == 'openai' and self.openai_client:
            return self._call_openai(model, messages, temperature, max_tokens, stream, **kwargs)
        elif provider == 'claude' and self.claude_client:
            return self._call_claude_as_openai(model, messages, temperature, max_tokens, **kwargs)
        else:
            # raise ValueError(f"不支持的提供商: {provider} 或客户端未初始化")
            return self._call_openai(model, messages, temperature, max_tokens, stream, **kwargs)
    
    def _call_openai(self, model: str, messages: List[Dict], temperature: float, 
                    max_tokens: Optional[int], stream: bool, **kwargs) -> Dict:
        """调用OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                timeout=120,
                **kwargs
            )
            
            if stream:
                return response
            
            return {
                "id": response.id,
                "object": "chat.completion",
                "created": response.created,
                "model": response.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.choices[0].message.content
                    },
                    "finish_reason": response.choices[0].finish_reason
                }],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            }
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {e}")
    
    def _call_claude_as_openai(self, model: str, messages: List[Dict], 
                              temperature: float, max_tokens: Optional[int], **kwargs) -> Dict:
        """将Claude API调用转换为OpenAI格式响应"""
        try:
            # 转换消息格式
            system_message = None
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # 调用Claude API
            claude_kwargs = {
                "model": model if 'claude' in model else "claude-3-5-sonnet-20241022",
                "max_tokens": max_tokens or 4000,
                "temperature": temperature,
                "messages": claude_messages
            }
            
            if system_message:
                claude_kwargs["system"] = system_message
            
            response = self.claude_client.messages.create(**claude_kwargs)
            
            # 转换为OpenAI格式
            return {
                "id": response.id,
                "object": "chat.completion",
                "created": int(response.created.timestamp()) if hasattr(response, 'created') else 0,
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content[0].text
                    },
                    "finish_reason": response.stop_reason or "stop"
                }],
                "usage": {
                    "prompt_tokens": response.usage.input_tokens if response.usage else 0,
                    "completion_tokens": response.usage.output_tokens if response.usage else 0,
                    "total_tokens": (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0
                }
            }
        except Exception as e:
            raise Exception(f"Claude API调用失败: {e}")
    
    def generate_response(self, 
                         system_prompt: str, 
                         user_prompt: str, 
                         model: str = "gpt-3.5-turbo",
                         max_tokens: int = 4000,
                         temperature: float = 0.7) -> str:
        """
        生成AI响应（向后兼容方法）
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            
        Returns:
            str: AI的响应
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        
        response = self.chat_completions_create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response["choices"][0]["message"]["content"]
    
    def generate_structured_response(self,
                                   system_prompt: str,
                                   user_prompt: str,
                                   model: str = "gpt-3.5-turbo",
                                   expected_structure: str = "json",
                                   max_tokens: int = 4000) -> Dict:
        """
        生成结构化响应
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            model: 模型名称
            expected_structure: 期望的响应结构格式
            max_tokens: 最大token数
            
        Returns:
            Dict: 解析后的结构化数据
        """
        # 在用户提示中明确要求结构化输出
        structured_prompt = f"{user_prompt}\n\n请以{expected_structure}格式返回结果。"
        
        response = self.generate_response(
            system_prompt=system_prompt,
            user_prompt=structured_prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=0.3  # 降低温度以获得更稳定的结构化输出
        )
        
        # 尝试解析JSON响应
        if expected_structure.lower() == "json":
            try:
                # 先尝试清理markdown代码块
                cleaned_response = response.strip()
                
                # 移除markdown代码块标记
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]  # 移除 ```json
                elif cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]   # 移除 ```
                
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]  # 移除结尾的 ```
                
                cleaned_response = cleaned_response.strip()
                
                # 提取JSON部分
                start_idx = cleaned_response.find('{')
                end_idx = cleaned_response.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = cleaned_response[start_idx:end_idx]
                    
                    # 尝试修复常见的JSON格式问题
                    # 1. 替换中文引号为英文引号
                    json_str = json_str.replace('"', '"').replace('"', '"')
                    json_str = json_str.replace(''', "'").replace(''', "'")
                    
                    # 先尝试直接解析
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # 如果失败，尝试修复引号问题
                        # 2. 处理未转义的引号问题
                        lines = json_str.split('\n')
                        fixed_lines = []
                        
                        for line in lines:
                            # 检查是否是JSON字符串值行
                            if '": "' in line and line.count('"') > 4:
                                # 尝试修复未转义的引号
                                value_start = line.find('": "') + 4
                                value_end = line.rfind('"')
                                
                                if value_start < value_end:
                                    value = line[value_start:value_end]
                                    # 计算值内部的引号数
                                    inner_quotes = value.count('"')
                                    
                                    if inner_quotes > 0:
                                        # 将内部的引号转义
                                        fixed_value = value.replace('"', '\\"')
                                        fixed_line = line[:value_start] + fixed_value + line[value_end:]
                                        fixed_lines.append(fixed_line)
                                        continue
                            
                            fixed_lines.append(line)
                        
                        fixed_json = '\n'.join(fixed_lines)
                        return json.loads(fixed_json)
                else:
                    # 如果没有找到JSON，尝试整个响应
                    return json.loads(cleaned_response)
                    
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"原始响应长度: {len(response)} 字符")
                print(f"原始响应前200字符: {response[:200]}...")
                
                # 尝试找到具体的错误位置
                try:
                    error_position = e.pos
                    if error_position:
                        print(f"错误位置附近的内容: {cleaned_response[max(0, error_position-50):error_position+50]}")
                except:
                    pass
                    
                return {
                    "error": "JSON解析失败",
                    "raw_response": response
                }
        
        return {"response": response}


# 为了向后兼容，保留原来的ClaudeClient类
class ClaudeClient(UnifiedAIClient):
    """Claude客户端（向后兼容）"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key, provider='claude')


class OpenaiClient(UnifiedAIClient):
    """OpenAI客户端 - 专门用于OpenAI API调用"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化OpenAI客户端
        
        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量OPENAI_API_KEY读取
            base_url: 自定义API端点URL，支持OpenAI兼容的API服务
        """
        super().__init__(api_key=api_key, base_url=base_url, provider='openai')
    
    def completions_create(self, 
                          model: str = "gpt-3.5-turbo",
                          messages: Optional[List[Dict[str, str]]] = None,
                          prompt: Optional[str] = None,
                          system_prompt: Optional[str] = None,
                          temperature: float = 0.7,
                          max_tokens: Optional[int] = None,
                          stream: bool = False,
                          **kwargs) -> Dict[str, Any]:
        """
        OpenAI风格的completions创建方法
        
        Args:
            model: 模型名称，默认为gpt-3.5-turbo
            messages: 消息列表（OpenAI格式）
            prompt: 单个提示文本（简化用法）
            system_prompt: 系统提示（简化用法）
            temperature: 温度参数
            max_tokens: 最大令牌数
            stream: 是否流式输出
            **kwargs: 其他参数
            
        Returns:
            Dict: OpenAI格式的响应
        """
        # 如果提供了prompt参数，构建messages
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if prompt:
                messages.append({"role": "user", "content": prompt})
            elif not messages:
                raise ValueError("必须提供messages或prompt参数")
        
        return self.chat_completions_create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
        )
    
    def simple_chat(self, 
                   prompt: str,
                   model: str = "gpt-3.5-turbo",
                   system_prompt: Optional[str] = None,
                   temperature: float = 0.7,
                   max_tokens: Optional[int] = None) -> str:
        """
        简化的聊天接口
        
        Args:
            prompt: 用户输入
            model: 模型名称
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            str: AI响应内容
        """
        response = self.completions_create(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response["choices"][0]["message"]["content"]


# 创建便捷的工厂函数
def create_openai_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> UnifiedAIClient:
    """创建OpenAI客户端"""
    return UnifiedAIClient(api_key=api_key, base_url=base_url, provider='openai')


def create_claude_client(api_key: Optional[str] = None) -> UnifiedAIClient:
    """创建Claude客户端"""
    return UnifiedAIClient(api_key=api_key, provider='claude')


def create_auto_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> UnifiedAIClient:
    """创建自动检测客户端"""
    return UnifiedAIClient(api_key=api_key, base_url=base_url, provider='auto') 