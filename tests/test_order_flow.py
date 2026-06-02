from playwright.sync_api import Page, expect


def test_order_flow(page: Page):
    """Basic order flow: navigate to Products and check product listing is visible."""
    page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
    page.get_by_text("Products").click()
    page.wait_for_url("**/products")
    expect(page.get_by_text("Features Items")).to_be_visible()
