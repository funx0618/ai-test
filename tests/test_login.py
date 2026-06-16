"""
test_login.py - 使用 LoginFlow 的登录测试

逻辑来源：test_login_flow.py 中的 test_login
区别：
  - 原始版本直接用 page API 逐步操作
  - 本版本通过 LoginFlow 一行完成登录，再用 LoginPage 断言验证

测试数据：从 data/test_users.json 加载
"""

from flows.login_flow import LoginFlow
from utils.data_loader import load_test_users, generate_random_user

USERS = load_test_users()


def test_login(page):
    login_flow = LoginFlow(page)
    user = USERS["login"]

    login_flow.login_as(
        email=user["email"],
        password=user["password"],
    )

    login_flow.verify_login(username=user["username"])


def test_existed_email(page):
    login_flow = LoginFlow(page)
    user = USERS["existed_email"]

    # Step 1: 打开登录页，填写已存在的邮箱并点击 Signup
    login_flow.open_login_page()
    login_flow.login_page.fill_signup(name=user["name"], email=user["email"])
    login_flow.login_page.submit_signup(expect_navigate=False)

    # Step 2: 验证提示（页面停留在登录页，不会跳转到注册页）
    login_flow.verify_email_already_exists()


def test_register_user(page):
    login_flow = LoginFlow(page)
    user = generate_random_user()

    # Step 1: 注册新用户
    login_flow.signup(
        name=user["name"],
        email=user["email"],
    )

    # Step 2: 验证注册成功
    login_flow.verify_register_success()


def test_delete_user(page):
    login_flow = LoginFlow(page)
    user = generate_random_user()

    # Step 1: 注册新用户
    login_flow.signup(
        name=user["name"],
        email=user["email"],
    )

    # Step 2: 验证注册成功（注册后网站自动登录）
    login_flow.verify_register_success()

    # Step 3: 点击 Continue 进入首页
    login_flow.login_page.continue_after_register()

    # Step 4: 验证已登录状态
    login_flow.verify_login(username=user["name"])

    # Step 5: 删除账户并验证删除成功
    login_flow.delete_account()


def test_login_error_password(page):
    """使用错误密码登录，验证登录失败"""
    login_flow = LoginFlow(page)
    user = USERS["login_error_password"]

    login_flow.login_as(
        email=user["email"],
        password=user["password"],
    )
    login_flow.verify_login_error()


def test_login_error_email(page):
    """使用错误邮箱登录，验证登录失败"""
    login_flow = LoginFlow(page)
    user = USERS["login_error_email"]

    login_flow.login_as(
        email=user["email"],
        password=user["password"],
    )
    login_flow.verify_login_error()


def test_logout(page):
    login_flow = LoginFlow(page)
    user = USERS["login"]

    # Step 1: 登录
    login_flow.login_as(
        email=user["email"],
        password=user["password"],
    )
    login_flow.verify_login(username=user["username"])

    # Step 2: 点击 Logout，验证回到登录页
    login_flow.logout()




