"""
LoginFlow - 登录 & 登出的复合业务流程

作用：
  - 将「打开首页 → 点击 Signup/Login → 输入账号密码 → 点击 Login」
    这个多页面、多步骤的操作封装成一个方法
  - 测试用例只需一行：login_flow.login_as("agent01@qq.com", "123456")

"""

import re
import random
import string
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage


class LoginFlow:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.login_page = LoginPage(page)

    def open_login_page(self) -> None:
        """从首页进入登录页"""
        self.login_page.open_via_homepage()

    def login_as(self, email: str, password: str) -> None:
        """完整登录流程：打开首页 → 进登录页 → 输入账号密码 → 点击 Login"""
        self.open_login_page()
        self.login_page.login(email, password)

    def login_and_verify(self, email: str, password: str, username: str) -> None:
        """登录并验证登录成功状态"""
        self.login_as(email, password)
        self.verify_login(username)

    def verify_login(self, username: str) -> None:
        """验证登录成功状态"""
        self.login_page.expect_logged_in(username)

    def verify_email_already_exists(self) -> None:
        """验证邮箱已存在的错误提示"""
        self.login_page.expect_email_already_exists()

    def logout(self) -> None:
        """点击 Logout"""
        self.page.get_by_role("link", name="Logout").click()
        expect(self.page).to_have_url(re.compile(r".*/login"))

    def signup(self, name: str, email: str) -> None:
        """完整注册第一步流程：打开首页 → 进登录页 → 填 name/email → 点 Signup → 填账户详情"""
        self.open_login_page()
        self.login_page.fill_signup(name, email)
        self.login_page.submit_signup()

        # 随机生成账户详情
        rand_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.login_page.fill_account_details(
            password="123456",
            first_name=f"FN_{rand_id}",
            last_name=f"LN_{rand_id}",
            company=f"Company_{rand_id}",
            address=f"{random.randint(1, 999)} Test Street",
            address2=f"Apt {random.randint(1, 99)}",
            city=f"City_{rand_id}",
            state=f"State_{rand_id}",
            zipcode=str(random.randint(10000, 99999)),
            mobile=f"1{random.randint(1000000000, 9999999999)}",
            day=str(random.randint(1, 28)),
            month=random.choice([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December",
            ]),
            year=str(random.randint(1970, 2000)),
        )
        self.login_page.submit_create_account()

    def verify_register_success(self) -> None:
        """验证注册成功"""
        self.login_page.expect_account_created()

    def delete_account(self) -> None:
        """删除账户并验证删除成功"""
        self.login_page.delete_account()
        self.login_page.expect_account_deleted()
        self.login_page.continue_after_delete()
