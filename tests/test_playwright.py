from playwright.sync_api import sync_playwright, expect
def test_image():
    with (sync_playwright() as p):
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.saucedemo.com/", wait_until="domcontentloaded")
        page.get_by_placeholder("Username").fill("standard_user")
        page.get_by_role("textbox", name="Password").fill("secret_sauce")
        page.get_by_role("button", name="Login").click()
        expect(page).to_have_url(
            "https://www.saucedemo.com/inventory.html"
        )
        page.get_by_alt_text("Sauce Labs Fleece Jacket").click()
        # page.get_by_role("image", name="Sauce Labs Fleece Jacket").click()

