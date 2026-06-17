"""
ai/config.py - LLM Configuration

支持两种 LLM 后端：
  - Xiaomi MiMo (mimo-v2.5-pro) ← 当前默认
  - OpenAI (GPT-4o, GPT-4, etc.)

配置方式（按优先级）：
  1. 环境变量
  2. .env 文件（项目根目录）
  3. 本文件中的默认值

安全提示：
  API Key 通过 .env 文件或环境变量传入，不要硬编码在源码中！
  .env 文件已加入 .gitignore，不会被提交到版本控制。
"""

import os
from pathlib import Path

# 自动加载 .env 文件
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv 未安装时忽略，依赖系统环境变量

# ========== LLM Provider ==========
# 可选值: mimo | openai
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mimo")

# ========== Xiaomi MiMo ==========
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "")
MIMO_MODEL = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

# ========== OpenAI ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# ========== Analysis Settings ==========
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
