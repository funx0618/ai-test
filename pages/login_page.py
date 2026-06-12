"""
LoginPage - 注册 & 登录页面对象，只负责页面交互，不负责业务流程

作用：
  - 封装 automationexercise.com 的 Signup / Login 页面所有交互
  - 包括：登录，注册（第一步填 name/email，第二步填账户详情）、
          登录、错误信息断言、删除账户？等

"""

import re
from playwright.sync_api import expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"
    PAGE_NAME = "LoginPage"

    # ========== 注册（第一步 — 登录页上的 Signup 表单）==========
    SIGNUP_NAME = "[data-qa='signup-name']"
    SIGNUP_EMAIL = "[data-qa='signup-email']"
    SIGNUP_BTN = "[data-qa='signup-button']"

    # ========== 登录表单 ==========
    LOGIN_EMAIL = "[data-qa='login-email']"
    LOGIN_PWD = "[data-qa='login-password']"
    LOGIN_BTN = "[data-qa='login-button']"

    # ========== 注册（第二步 — 账户详情表单）==========
    PASSWORD = "[data-qa='password']"
    DAYS = "[data-qa='days']"
    MONTHS = "[data-qa='months']"
    YEARS = "[data-qa='years']"
    FIRST_NAME = "[data-qa='first_name']"
    LAST_NAME = "[data-qa='last_name']"
    COMPANY = "[data-qa='company']"
    ADDRESS = "[data-qa='address']"
    ADDRESS2 = "[data-qa='address2']"
    COUNTRY = "[data-qa='country']"
    STATE = "[data-qa='state']"
    CITY = "[data-qa='city']"
    ZIPCODE = "[data-qa='zipcode']"
    MOBILE = "[data-qa='mobile_number']"
    CREATE_ACCOUNT_BTN = "[data-qa='create-account']"

    # ========== 错误 / 信息消息 ==========
    MSG_EMAIL_EXISTS = "Email Address already exist!"
    MSG_LOGIN_ERROR = "Your email or password is incorrect!"
    MSG_ACCOUNT_DELETED = "Account Deleted!"

    # ========== 导航 ==========
    def open(self) -> None:
        self.page.goto(f"{self.BASE_URL}{self.URL}", wait_until="domcontentloaded")

    def open_via_homepage(self) -> None:
        """从首页点击 Signup / Login 进入登录页"""
        self.page.goto(f"{self.BASE_URL}/", wait_until="domcontentloaded")
        self.page.get_by_role("link", name="Signup / Login").click()
        expect(self.page).to_have_url(re.compile(r".*/login"))

    # ========== 注册（第一步）==========
    def fill_signup(self, name: str, email: str) -> None:
        self.page.locator(self.SIGNUP_NAME).fill(name)
        self.page.locator(self.SIGNUP_EMAIL).fill(email)

    def submit_signup(self) -> None:
        self.page.get_by_role("button", name="Signup").click()
        expect(self.page).to_have_url(re.compile(r".*/signup"))

    # signup() 已移至 LoginFlow，由 Flow 层负责完整的第一步注册流程

    # ========== 注册（第二步 — 账户详情）==========
    def fill_account_details(
        self,
        password: str = "123456",
        first_name: str = "",
        last_name: str = "",
        company: str = "",
        address: str = "",
        address2: str = "",
        city: str = "",
        state: str = "",
        zipcode: str = "",
        mobile: str = "",
        day: str = "1",
        month: str = "January",
        year: str = "2000",
        country: str = "United States",
    ) -> None:
        self.page.locator(self.PASSWORD).fill(password)
        self.page.locator(self.DAYS).select_option(value=day)
        self.page.locator(self.MONTHS).select_option(value=month)
        self.page.locator(self.YEARS).select_option(value=year)
        self.page.locator(self.FIRST_NAME).fill(first_name)
        self.page.locator(self.LAST_NAME).fill(last_name)
        self.page.locator(self.COMPANY).fill(company)
        self.page.locator(self.ADDRESS).fill(address)
        self.page.locator(self.ADDRESS2).fill(address2)
        self.page.locator(self.COUNTRY).select_option(value=country)
        self.page.locator(self.STATE).fill(state)
        self.page.locator(self.CITY).fill(city)
        self.page.locator(self.ZIPCODE).fill(zipcode)
        self.page.locator(self.MOBILE).fill(mobile)

    def submit_create_account(self) -> None:
        self.page.locator(self.CREATE_ACCOUNT_BTN).click()

    # ========== 登录 ==========
    def login(self, email: str, password: str) -> None:
        self.page.locator(self.LOGIN_EMAIL).fill(email)
        self.page.locator(self.LOGIN_PWD).fill(password)
        # 优先用 data-qa，如果页面没有则用 role
        if self.page.locator(self.LOGIN_BTN).count() > 0:
            self.page.locator(self.LOGIN_BTN).click()
        else:
            self.page.get_by_role("button", name="Login").click()

    # ========== 错误断言 ==========
    def expect_account_created(self) -> None:
        expect(self.page.get_by_text("Account Created!")).to_be_visible()
        expect(self.page.get_by_text("Congratulations! Your new account has been successfully created!")).to_be_visible()
        expect(self.page.locator("[data-qa='continue-button']")).to_be_visible()

    def expect_email_already_exists(self) -> None:
        expect(self.page.get_by_text(self.MSG_EMAIL_EXISTS)).to_be_visible()

    def expect_login_error(self) -> None:
        expect(self.page.get_by_text(self.MSG_LOGIN_ERROR)).to_be_visible()

    # ========== 登录后状态断言 ==========
    def expect_logged_in(self, username: str) -> None:
        expect(self.page.get_by_text(f"Logged in as {username}")).to_be_visible()
        expect(self.page.get_by_role("link", name="Logout")).to_be_visible()
        expect(self.page.get_by_role("link", name="Delete Account")).to_be_visible()

    # ========== 删除账户 ==========
    def delete_account(self) -> None:
        self.page.get_by_role("link", name="Delete Account").click()

    def expect_account_deleted(self) -> None:
        expect(self.page.get_by_text("Account Deleted!")).to_be_visible()
        expect(self.page.get_by_text("Your account has been permanently deleted!")).to_be_visible()

    def continue_after_delete(self) -> None:
        self.page.get_by_role("link", name="Continue").click()
        self.page.wait_for_url("**/")
