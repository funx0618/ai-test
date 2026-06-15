"""
User fixtures - 用户数据 & 预登录会话

作用：
  - 提供 default_user fixture（从硬编码或 data/users.json 加载测试账号）
  - 提供 logged_in_page fixture（返回已登录状态的 page，省去每个 test 手动登录）

为什么需要这一层：
  - test_login_flow.py 中，agent01@qq.com / 123456 出现了 5 次
  - 把账号信息集中管理，换账号只改一处
  - logged_in_page 让需要登录态的 test 直接拿到已登录的 page，不用重复写登录步骤
"""

import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage
from flows.login_flow import LoginFlow


# ========== 测试账号数据 ==========
# 后续可改为从 data/users.json 读取
DEFAULT_USER = {
    "name": "agent01",
    "email": "agent01@qq.com",
    "password": "123456",
    "username": "agent01",
}



@pytest.fixture
def default_user() -> dict:
    """返回默认测试用户信息。"""
    return DEFAULT_USER


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """返回 LoginPage 实例，绑定到当前 test 的 page。"""
    return LoginPage(page)


@pytest.fixture
def login_flow(page: Page) -> LoginFlow:
    """返回 LoginFlow 实例，绑定到当前 test 的 page。"""
    return LoginFlow(page)


@pytest.fixture
def logged_in_page(page: Page, default_user: dict) -> Page:
    """
    返回已登录状态的 page。

    用法：
        def test_something(logged_in_page):
            # page 已经登录了，直接操作即可
            logged_in_page.get_by_role("link", name="Logout")
    """
    flow = LoginFlow(page)
    flow.login_and_verify(
        email=default_user["email"],
        password=default_user["password"],
        username=default_user["username"],
    )
    return page
