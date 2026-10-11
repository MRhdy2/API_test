"""
这是一个大模型分析器，用于在自动化测试失败时，

把测试用例名和错误堆栈发送给大模型（如通义千问、OpenAI 兼容接口），

让模型给出根因分析和修复建议。
"""

import asyncio
import json
import requests
import time
from typing import Optional, Dict, Any


class LLMAnalyzer:
    """大模型分析器，用于分析测试报错并提供修复建议"""

    def __init__(self, api_key: str, model: str, base_url: str, timeout: int = 30):
        """初始化大模型分析器

        Args:
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL
            timeout: 超时时间（秒）
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        print(f"[调试] 初始化LLMAnalyzer时的base_url: {base_url}")

    def analyze_error_sync(self, test_name: str, traceback: str) -> Optional[str]:
        """同步分析测试错误

        Args:
            test_name: 测试用例名称
            traceback: 错误堆栈信息

        Returns:
            分析结果字符串，失败返回None
        """
        try:
            prompt = self._generate_prompt(test_name, traceback)
            response = self._call_llm_api(prompt)
            return self._format_response(response)
        except Exception as e:
            print(f"[LLM分析错误]: {str(e)}")
            return None

    async def analyze_error_async(self, test_name: str, traceback: str) -> Optional[str]:
        """异步分析测试错误

        Args:
            test_name: 测试用例名称
            traceback: 错误堆栈信息

        Returns:
            分析结果字符串，失败返回None
        """
        try:
            prompt = self._generate_prompt(test_name, traceback)
            response = await self._call_llm_api_async(prompt)
            return self._format_response(response)
        except Exception as e:
            print(f"[LLM分析错误]: {str(e)}")
            return None

    def _generate_prompt(self, test_name: str, traceback: str) -> str:
        """生成大模型提示词

        Args:
            test_name: 测试用例名称
            traceback: 错误堆栈信息

        Returns:
            提示词字符串
        """
        return f"""
你是一位专业的Python测试工程师，擅长分析测试报错并提供修复建议。

请分析以下测试用例的错误信息，提供详细的根因分析和修复建议：

测试用例名称: {test_name}

错误堆栈信息:
{traceback}

请按照以下格式输出分析结果：
1. 根因分析：详细分析错误的根本原因
2. 修复建议：提供具体的修复方案
3. 代码示例：如果适用，提供修复后的代码示例
4. 预防措施：如何避免类似错误再次发生

请确保分析结果详细、准确、实用，帮助开发者快速定位和解决问题。
"""

    def _call_llm_api(self, prompt: str) -> Dict[str, Any]:
        """调用大模型API（同步）

        Args:
            prompt: 提示词

        Returns:
            API响应结果
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 10000
        }

        # 构建endpoint：如果是新的兼容模式URL，直接使用；否则拼接/chat/completions
        if "compatible-mode" in self.base_url and self.base_url.endswith("/v1"):
            endpoint = f"{self.base_url}/chat/completions"
        else:

            endpoint = f"{self.base_url}/chat/completions"

        response = requests.post(
            endpoint,
            headers=self.headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    async def _call_llm_api_async(self, prompt: str) -> Dict[str, Any]:
        """调用大模型API（异步）

        Args:
            prompt: 提示词

        Returns:
            API响应结果
        """
        import aiohttp


        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 10000
        }

        # 构建endpoint：如果是新的兼容模式URL，直接使用；否则拼接/chat/completions
        if "compatible-mode" in self.base_url and self.base_url.endswith("/v1"):
            endpoint = f"{self.base_url}/chat/completions"
        else:

            endpoint = f"{self.base_url}/chat/completions"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                return await response.json()

    def _format_response(self, response: Dict[str, Any]) -> str:
        """格式化API响应

        Args:
            response: API响应结果

        Returns:
            格式化后的分析结果
        """
        try:
            # 提取模型回复内容
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0].get("message", {}).get("content", "")
                return content
            return ""
        except Exception as e:
            print(f"[响应格式化错误]: {str(e)}")
            return ""
