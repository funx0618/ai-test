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

    # Step 1: 打开登录页，填写已存在的邮箱并点击 Signup
    login_flow.open_login_page()
    login_flow.login_page.fill_signup(name="agent01", email="agent01@qq.com")
    login_flow.login_page.submit_signup(expect_navigate=False)

    # Step 2: 验证提示（页面停留在登录页，不会跳转到注册页）
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


def test_delete_user(page):
    login_flow = LoginFlow(page)

    # Step 1: 注册新用户
    login_flow.signup(
        name="agent10",
        email="agent10@qq.com",
    )

    # Step 2: 验证注册成功（注册后网站自动登录）
    login_flow.verify_register_success()

    # Step 3: 点击 Continue 进入首页
    login_flow.login_page.continue_after_register()

    # Step 4: 验证已登录状态
    login_flow.verify_login(username="agent10")

    # Step 5: 删除账户并验证删除成功
    login_flow.delete_account()


def test_login_error(page):
    login_flow = LoginFlow(page)

    # 情况1：错误的密码
    login_flow.login_as(
        email="agent01@qq.com",
        password="1234",
    )
    login_flow.verify_login_error()

    # 情况2：错误的 email
    login_flow.login_as(
        email="wrong@qq.com",
        password="123456",
    )
    login_flow.verify_login_error()


def test_logout(page):
    login_flow = LoginFlow(page)

    # Step 1: 登录
    login_flow.login_as(
        email="agent01@qq.com",
        password="123456",
    )
    login_flow.verify_login(username="agent01")

    # Step 2: 点击 Logout，验证回到登录页
    login_flow.logout()




