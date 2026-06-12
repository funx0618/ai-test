"""
BasePage - 所有页面对象的基类

作用：
  - 提供 BASE_URL，子类继承后可直接使用 self.page 调用 Playwright API
  - 所有 Page 类继承此基类，共享 BASE_URL 配置
"""

class BasePage:
    BASE_URL: str = "https://automationexercise.com"

    def __init__(self, page) -> None:
        self.page = page
