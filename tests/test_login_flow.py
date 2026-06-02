import random
import string
import time
from playwright.sync_api import Page, expect


def _rand_str(n=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def test_create_user(page: Page):
    # Open homepage and navigate to Signup / Login page
    page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
    page.get_by_text("Signup / Login").click()
    page.wait_for_url("**/login")

    # Keep references to the Name and Email inputs on the login page
    name_input = page.locator("[data-qa='signup-name']")
    email_input = page.locator("[data-qa='signup-email']")

    # Fill Name and Email on the login/signup page
    name_input.fill("agent01")
    email_input.fill("agent01@qq.com")

    # Proceed from the "Signup / Login" page to the signup details page
    page.get_by_role("button", name="Signup").click()

    # Wait for signup detail page
    page.wait_for_url("**/signup")
    # NOTE: Name and Email are preserved from the previous login/signup form
    # Do not re-fill Name/Email on this page.

    # Account details
    password = "123456"
    first_name = "FN" + _rand_str(5)
    last_name = "LN" + _rand_str(5)
    company = "Co" + _rand_str(4)
    address = f"Addr {_rand_str(6)}"
    address2 = f"Addr2 {_rand_str(4)}"
    city = "City" + _rand_str(4)
    state = "State" + _rand_str(3)
    zipcode = ''.join(random.choices(string.digits, k=5))
    mobile = ''.join(random.choices(string.digits, k=10))

    # Fill fields using data-qa attributes
    page.locator("[data-qa='password']").fill(password)

    # date selects (data-qa) - use locator().select_option(...) for better readability
    page.locator("[data-qa='days']").select_option("1")
    page.locator("[data-qa='months']").select_option("1")
    page.locator("[data-qa='years']").select_option("2000")

    page.locator("[data-qa='first_name']").fill(first_name)
    page.locator("[data-qa='last_name']").fill(last_name)
    page.locator("[data-qa='company']").fill(company)
    page.locator("[data-qa='address']").fill(address)
    page.locator("[data-qa='address2']").fill(address2)

    # country select by data-qa - use locator().select_option with value 'United States'
    page.locator("[data-qa='country']").select_option(value="United States")

    page.locator("[data-qa='state']").fill(state)
    page.locator("[data-qa='city']").fill(city)
    page.locator("[data-qa='zipcode']").fill(zipcode)
    page.locator("[data-qa='mobile_number']").fill(mobile)

    # Click Create Account (use data-qa)
    page.locator("[data-qa='create-account']").click()


def test_existed_email(page: Page):
    # Verify behavior when the email already exists
    page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
    page.get_by_text("Signup / Login").click()
    page.wait_for_url("**/login")

    page.locator("[data-qa='signup-name']").fill("agent01")
    page.locator("[data-qa='signup-email']").fill("agent01@qq.com")

    page.get_by_role("button", name="Signup").click()

    expect(page.get_by_text("Email Address already exist!")).to_be_visible()


def test_login_error(page: Page):
    # Attempt login with wrong password and assert error message
    page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
    page.get_by_text("Signup / Login").click()
    page.wait_for_url("**/login")
    # 1) Wrong password for existing email
    page.locator("[data-qa='login-email']").fill("agent01@qq.com")
    page.locator("[data-qa='login-password']").fill("12344")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("Your email or password is incorrect!")).to_be_visible()

    # 2) Wrong/non-existent email with a valid-looking password
    page.locator("[data-qa='login-email']").fill("nonexist_user_123@qq.com")
    page.locator("[data-qa='login-password']").fill("123456")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("Your email or password is incorrect!")).to_be_visible()

  



  
def test_login(page: Page):
    # Log in with existing user and verify top-right account controls
    page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
    page.get_by_text("Signup / Login").click()
    page.wait_for_url("**/login")

    page.locator("[data-qa='login-email']").fill("agent01@qq.com")
    page.locator("[data-qa='login-password']").fill("123456")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_role("link", name="Logout")).to_be_visible()
    expect(page.get_by_role("link", name="Delete Account")).to_be_visible()
    expect(page.get_by_text("Logged in as agent01")).to_be_visible()


def test_delete_account(page: Page):
    # Log in as the existing account, delete it, and verify post-delete UI
    page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
    page.get_by_text("Signup / Login").click()
    page.wait_for_url("**/login")

    page.locator("[data-qa='login-email']").fill("agent01@qq.com")
    page.locator("[data-qa='login-password']").fill("123456")
    page.get_by_role("button", name="Login").click()

    # Click Delete Account (top-right link)
    page.get_by_role("link", name="Delete Account").click()

    # Verify account deletion messages
    expect(page.get_by_text("Account Deleted!")).to_be_visible()
    expect(page.get_by_text("Your account has been permanently deleted!")).to_be_visible()

    # Logout and the "Logged in as agent01" indicator should no longer be present
    expect(page.get_by_role("link", name="Logout")).to_have_count(0)
    expect(page.get_by_text("Logged in as agent01")).to_have_count(0)

    # Click Continue and verify we return to home
    page.get_by_role("link", name="Continue").click()
    page.wait_for_url("**/")
