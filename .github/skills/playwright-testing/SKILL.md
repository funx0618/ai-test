---
name: playwright-testing
description: 'Playwright + pytest 自动化测试技能。用于：创建新测试用例、新增 Page Object、新增 Flow 业务流程、调试测试失败、理解项目测试架构。USE FOR: writing new test cases, adding page objects, creating flows, debugging failures, understanding POM structure.'
argument-hint: '描述你要创建或修改的测试内容'
---

# Playwright 自动化测试技能

## 项目概览

- **目标网站**: https://automationexercise.com
- **技术栈**: Python + pytest + Playwright
- **架构模式**: Page Object Model (POM) + Flow 层
- **运行命令**: `pytest tests/<file>.py::<test_name> -v`

## 项目结构

```
├── conftest.py              # pytest hooks（失败时自动截图/trace）
├── pytest.ini               # pytest 配置
├── fixtures/
│   ├── browser_fixture.py   # browser/context/page fixture（session 级浏览器，test 级页面）
│   └── user_fixture.py      # 用户相关 fixture
├── pages/                   # Page Object 层 —— 只负责页面元素交互
│   ├── base_page.py         # 基类，提供 BASE_URL
│   └── <module>_page.py     # 各页面对象（login_page, products_page 等）
├── flows/                   # Flow 层 —— 组合多个 Page 操作成业务流程
│   └── <module>_flow.py     # 各业务流程（login_flow, order_flow 等）
├── tests/                   # 测试用例层
│   └── test_<module>.py     # 测试文件
├── data/                    # 测试数据
├── reports/                 # 测试报告
├── screenshots/             # 失败时自动截图
└── traces/                  # 失败时自动 trace
```

## 三层架构规范

### 1. Page 层（`pages/`）— 元素定位 + 原子操作

```python
"""
<PageName>Page - <页面描述>

作用：
  - 封装 <网站名> 的 <页面> 所有交互
"""

import re
from playwright.sync_api import expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"                          # 页面路径
    PAGE_NAME = "LoginPage"

    # ========== 元素定位（用常量管理）==========
    LOGIN_EMAIL = "[data-qa='login-email']"
    LOGIN_PWD = "[data-qa='login-password']"
    LOGIN_BTN = "[data-qa='login-button']"

    # ========== 操作方法（原子级）==========
    def open(self) -> None:
        """直接打开页面"""
        self.page.goto(f"{self.BASE_URL}{self.URL}", wait_until="domcontentloaded")

    def open_via_homepage(self) -> None:
        """从首页导航到此页面"""
        self.page.goto(f"{self.BASE_URL}/", wait_until="domcontentloaded")
        self.page.get_by_role("link", name="Signup / Login").click()
        expect(self.page).to_have_url(re.compile(r".*/login"))

    def login(self, email: str, password: str) -> None:
        """填写登录表单并提交"""
        self.page.locator(self.LOGIN_EMAIL).fill(email)
        self.page.locator(self.LOGIN_PWD).fill(password)
        self.page.locator(self.LOGIN_BTN).click()

    # ========== 断言方法（expect_ 前缀）==========
    def expect_logged_in(self, username: str) -> None:
        expect(self.page.get_by_text(f"Logged in as {username}")).to_be_visible()

    def expect_login_error(self) -> None:
        expect(self.page.get_by_text("Your email or password is incorrect!")).to_be_visible()
```

**Page 层规则**:
- 继承 `BasePage`，使用 `self.BASE_URL` 和 `self.page`
- 元素定位用类常量（CSS selector 或 data-qa）
- 方法是原子操作：填表单、点击、断言
- 断言方法以 `expect_` 命名，使用 Playwright 的 `expect`
- 不包含业务流程逻辑（如"先登录再删除"）

### 2. Flow 层（`flows/`）— 组合 Page 操作成业务流程

```python
"""
LoginFlow - 登录 & 注册的复合业务流程

作用：
  - 将多个 Page 操作组合成完整的业务流程
  - 测试用例只需一行调用
"""

from playwright.sync_api import Page
from pages.login_page import LoginPage


class LoginFlow:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.login_page = LoginPage(page)

    def login_as(self, email: str, password: str) -> None:
        """完整登录流程：打开首页 → 进登录页 → 输入账号密码 → 点击 Login"""
        self.open_login_page()
        self.login_page.login(email, password)

    def verify_login(self, username: str) -> None:
        """验证登录成功状态"""
        self.login_page.expect_logged_in(username)

    def signup(self, name: str, email: str) -> None:
        """完整注册流程：打开首页 → 填表单 → 提交"""
        self.open_login_page()
        self.login_page.fill_signup(name, email)
        self.login_page.submit_signup()
        # ... 填写账户详情 ...
        self.login_page.submit_create_account()

    def delete_account(self) -> None:
        """删除账户并验证"""
        self.login_page.delete_account()
        self.login_page.expect_account_deleted()
        self.login_page.continue_after_delete()
```

**Flow 层规则**:
- 持有 Page 对象实例（`self.login_page = LoginPage(page)`）
- 方法是业务流程：组合多个 Page 操作
- 验证方法以 `verify_` 命名
- Flow 可以调用其他 Flow

### 3. Test 层（`tests/`）— 测试用例

```python
from flows.login_flow import LoginFlow


def test_login(page):
    login_flow = LoginFlow(page)

    # 操作
    login_flow.login_as(email="agent01@qq.com", password="123456")

    # 验证
    login_flow.verify_login(username="agent01")


def test_delete_user(page):
    login_flow = LoginFlow(page)

    # Step 1: 注册新用户（注册后自动登录）
    login_flow.signup(name="agent05", email="agent05@qq.com")
    login_flow.verify_register_success()

    # Step 2: 点击 Continue 进入首页
    login_flow.login_page.continue_after_register()

    # Step 3: 验证已登录 → 删除账户
    login_flow.verify_login(username="agent05")
    login_flow.delete_account()
```

**Test 层规则**:
- 使用 `page` fixture（每个测试独立的页面实例）
- 通过 Flow 调用业务操作，不直接操作 Page
- 每个测试独立，不依赖其他测试的执行顺序
- 测试内完成完整的生命周期（创建→操作→验证→清理）

## 关键约定

### 注册后自动登录
网站注册成功后**自动登录**，不需要再调用 `login_as`。注册成功页面点击 Continue 即可进入已登录首页。

### 页面导航等待策略
```python
# ✅ 推荐：domcontentloaded 更快更可靠
self.page.goto(url, wait_until="domcontentloaded")
self.page.wait_for_url("**/", wait_until="domcontentloaded")

# ❌ 避免：默认 load 等待所有资源，容易超时
self.page.wait_for_url("**/")
```

### 元素定位优先级
1. `[data-qa='xxx']` — 最稳定，网站自带的测试属性
2. `get_by_role("link", name="xxx")` — 语义化定位
3. `get_by_text("xxx")` — 文本定位（断言常用）
4. CSS selector — 兜底方案

### 失败调试
测试失败时自动保存到：
- `screenshots/<test_name>_<timestamp>.png` — 失败截图
- `traces/<test_name>_<timestamp>.zip` — Playwright trace（用 `playwright show-trace` 打开）

## 创建新测试的步骤

1. **分析页面**：确定需要哪些元素交互 → 写在 `pages/<page>_page.py`
2. **封装流程**：将多个页面操作组合 → 写在 `flows/<module>_flow.py`
3. **编写测试**：调用 Flow 方法 → 写在 `tests/test_<module>.py`
4. **运行验证**：`pytest tests/test_<module>.py::<test_name> -v`

## 新增 Page Object 模板

```python
"""
<PageName>Page - <页面描述>
"""
import re
from playwright.sync_api import expect
from pages.base_page import BasePage


class XxxPage(BasePage):
    URL = "/xxx"
    PAGE_NAME = "XxxPage"

    # 元素定位
    ELEMENT = "[data-qa='element']"

    # 页面操作
    def open(self) -> None:
        self.page.goto(f"{self.BASE_URL}{self.URL}", wait_until="domcontentloaded")

    def do_something(self) -> None:
        self.page.locator(self.ELEMENT).click()

    # 断言
    def expect_success(self) -> None:
        expect(self.page.get_by_text("Success!")).to_be_visible()
```

## 新增 Flow 模板

```python
"""
XxxFlow - <业务流程描述>
"""
from playwright.sync_api import Page
from pages.xxx_page import XxxPage


class XxxFlow:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.xxx_page = XxxPage(page)

    def complete_action(self) -> None:
        """完整的业务操作流程"""
        self.xxx_page.open()
        self.xxx_page.do_something()

    def verify_result(self) -> None:
        """验证操作结果"""
        self.xxx_page.expect_success()
```
