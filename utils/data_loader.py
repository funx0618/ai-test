"""
data_loader.py - 测试数据加载工具

作用：
  - 提供从 data/ 目录加载 JSON 测试数据的便捷函数
  - 统一管理测试数据路径，避免各测试文件重复写加载逻辑
"""

import json
import random
import string
from pathlib import Path

# data 目录路径
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename: str) -> dict:
    """从 data/ 目录加载 JSON 文件并返回字典。"""
    filepath = DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_test_users() -> dict:
    """加载用户测试数据。"""
    return load_json("test_users.json")


def load_test_products() -> dict:
    """加载产品测试数据。"""
    return load_json("test_products.json")


def generate_random_user() -> dict:
    """生成随机用户数据，返回 {"name": "agentXXX", "email": "agentXXX@qq.com"}。"""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=3))
    name = f"agent{suffix}"
    return {"name": name, "email": f"{name}@qq.com"}
