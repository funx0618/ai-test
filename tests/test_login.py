"""
test_login.py - 使用 LoginFlow 的登录测试

逻辑来源：test_login_flow.py 中的 test_login
区别：
  - 原始版本直接用 page API 逐步操作
  - 本版本通过 LoginFlow 一行完成登录，再用 LoginPage 断言验证
"""

# from playwright.sync_api import Page
from flows.login_flow import LoginFlow


def test_login(page):
    login_flow = LoginFlow(page)

    login_flow.login_as(
        email="agent01@qq.com",
        password="123456",
    )

    login_flow.verify_login(username="agent01")


def test_existed_email(page):
    login_flow = LoginFlow(page)

    # Step 1: 用已存在的邮箱尝试注册
    login_flow.signup(
        name="agent01",
        email="agent01@qq.com",
    )

    # Step 2: 验证提示
    login_flow.verify_email_already_exists()


def test_register_user(page):
    login_flow = LoginFlow(page)

    # Step 1: 注册新用户
    login_flow.signup(
        name="agent04",
        email="agent04@qq.com",
    )

    # Step 2: 验证注册成功
    login_flow.verify_register_success()




