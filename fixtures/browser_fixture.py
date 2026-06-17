"""
Browser & Page fixtures - 浏览器生命周期管理

作用：
  - 提供 session 级别的 browser 实例（整个测试会话共享）
  - 提供 test 级别的 context 和 page 实例（每个 test 独立隔离）

为什么需要这一层：
  - 原来的 test 中，page fixture 是 pytest-playwright 插件默认提供的
  - 把浏览器配置（headless/viewport/slow_mo）集中管理，方便切换环境
  - 后续可以方便地扩展：加 cookie、登录态预注入等
"""

import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def browser():
    """Session 级别的浏览器实例，所有测试共享。"""
    with sync_playwright() as p:
        br = p.chromium.launch(
            headless=False,      # 改为 True 可无头运行
            slow_mo=0,           # 毫秒，调试时可加大（如 200）
        )
        yield br
        br.close()


@pytest.fixture
def context(browser: Browser) -> BrowserContext:
    """每个 test 独立的浏览器上下文（隔离 cookies/localStorage）。"""
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
    )
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """每个 test 独立的 Page 实例 — 测试用例通过此 fixture 获取 page。"""
    p = context.new_page()
    yield p
