# -*- coding: utf-8 -*-
import time

import pytest
import warnings

from base import removefile
from common.dingRobot import send_dd_msg
from common.readyaml import ReadYamlData
from conf.setting import dd_msg

yfd = ReadYamlData()

import os
import sys
import allure
import pytest
from openai import OpenAI  # 需要安装 openai 包


def configure_utf8_output():
    """统一 pytest 进程及其子进程的标准输出编码为 UTF-8。"""
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


configure_utf8_output()


def load_local_env():
    """加载项目根目录的本地环境变量文件。"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ.setdefault(key.strip(), value)


load_local_env()

# 优先读取 DeepSeek 官方配置，同时兼容原有的密钥变量名。
API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("ALIYUN_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

# 配置了 API Key 时才启用 AI 失败分析，避免阻塞普通测试启动。
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
) if API_KEY else None

def call_deepseek(traceback_text):
    """调用 DeepSeek 官方 API 生成修复建议。"""
    if client is None:
        return "未配置 DEEPSEEK_API_KEY，已跳过 AI 失败分析。"

    prompt = f"""
你是一个 Python 测试专家。请分析以下 pytest 测试失败时的 traceback，并给出简明的修复建议。请用中文回答，保持友好且专业。

Traceback:
{traceback_text}
"""
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个 Python 测试专家。请根据实际报错代码准确定位原因，"
                        "给出 1 至 3 条可执行的修复建议，中文回答且不超过 300 字。"
                    ),
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
            # 失败分析只需要简短结论，关闭默认思考模式以免推理 token
            # 占满 max_tokens，导致最终 content 为空。
            extra_body={"thinking": {"type": "disabled"}},
        )
        message = completion.choices[0].message
        answer = message.content or getattr(message, "reasoning_content", None)
        if not answer:
            return "DeepSeek 请求成功，但没有返回可显示的分析内容。"
        return answer.strip()
    except Exception as e:
        return f"调用 AI 失败：{str(e)}"


def print_ai_suggestion(suggestion):
    """使用 UTF-8 安全输出 DeepSeek 建议。"""
    configure_utf8_output()
    message = f"\nAI 建议：\n{suggestion}\n"
    print(message)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # 保留具体出错代码，而不只是最后一行异常摘要；限制长度以控制费用。
        traceback_text = str(report.longrepr)[-12000:]

        suggestion = call_deepseek(traceback_text)
        print_ai_suggestion(suggestion)
        allure.attach(
            suggestion,
            name="DeepSeek 失败分析与修复建议",
            attachment_type=allure.attachment_type.TEXT,
        )
