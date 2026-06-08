import time
from playwright.sync_api import Page, expect


def test_home_subscription(page: Page):
    # 1) Log in as agent01
    page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
    page.get_by_text("Signup / Login").click()
    page.wait_for_url("**/login")

    page.locator("[data-qa='login-email']").fill("agent01@qq.com")
    page.locator("[data-qa='login-password']").fill("123456")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_role("link", name="Logout")).to_be_visible()

        # ---- Scroll to bottom (Home page) ----
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)") # 直接滚动到页面底部
    expect(page.locator("#susbscribe_email")).to_be_visible()
    # ---- Subscription section ----
    subscription_email = "2660185828@qq.com"

    page.fill("#susbscribe_email", subscription_email)
    page.click("#subscribe")

    # ---- Assertion ----
    success_msg = page.locator(".alert-success")

    expect(success_msg).to_contain_text(
        "You have been successfully subscribed!"
    )


def test_product_subscription(page: Page):
    # 1) Log in as agent01
    page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
    page.get_by_text("Signup / Login").click()
    page.wait_for_url("**/login")

    page.locator("[data-qa='login-email']").fill("agent01@qq.com")
    page.locator("[data-qa='login-password']").fill("123456")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_role("link", name="Logout")).to_be_visible()

    # ---- Go to Products page ----
    page.get_by_role("link", name="Products").click()
    page.wait_for_url("**/products")

    # ---- Scroll to bottom (Products page) ----
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    expect(page.locator("#susbscribe_email")).to_be_visible()

    # ---- Subscription section ----
    subscription_email = "2660185828+product@qq.com"

    page.fill("#susbscribe_email", subscription_email)
    page.click("#subscribe")

    # ---- Assertion ----
    success_msg = page.locator(".alert-success")

    expect(success_msg).to_contain_text(
        "You have been successfully subscribed!"
    )