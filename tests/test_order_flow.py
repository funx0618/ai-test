from playwright.sync_api import Page, expect
from pathlib import Path
import random
import re


def test_search_order(page: Page):
	# Log in as agent01
	page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
	page.get_by_text("Signup / Login").click()
	page.wait_for_url("**/login")
	page.locator("[data-qa='login-email']").fill("agent01@qq.com")
	page.locator("[data-qa='login-password']").fill("123456")
	page.get_by_role("button", name="Login").click()

	# Navigate to Products and search for "winter top"
	page.get_by_role("link", name="Products").click()
	page.wait_for_url("**/products")
	# use known search input id when available
	if page.locator("#search_product").count() > 0:
		page.locator("#search_product").fill("winter top")
	else:
		page.get_by_placeholder("Search Products").fill("winter top")
	# click search
	if page.locator("#submit_search").count() > 0:
		page.locator("#submit_search").click()
	else:
		page.get_by_role("button", name="Search").click()

	# Click the first matching "View Product"
	page.get_by_text("View Product").first.click()
	page.wait_for_url("**/product_details/*")

	# Add to cart and view cart from the modal
	# Try several selectors for robustness
	if page.get_by_role("button", name="Add to cart").count() > 0:
		page.get_by_role("button", name="Add to cart").click()
	else:
		page.locator("button:has-text('Add to cart')").click()

	# Wait for Added modal and click View Cart
	expect(page.get_by_text("Added!")).to_be_visible()
	# sometimes the button text is "View Cart"
	page.get_by_text("View Cart").click()
	page.wait_for_url("**/view_cart")
	# Proceed to checkout — use text selector
	page.get_by_text("Proceed To Checkout").first.click()
	page.wait_for_url("**/checkout")

	# Place the order — use link role
	page.get_by_role("link", name="Place Order").click()
	page.wait_for_url("**/payment")

	# Fill payment form using data-qa selectors (hyphenated names)
	page.locator("[data-qa='name-on-card']").fill("funx")
	page.locator("[data-qa='card-number']").fill("12345678")
	page.locator("[data-qa='cvc']").fill("311")
	page.locator("[data-qa='expiry-month']").fill("06")
	page.locator("[data-qa='expiry-year']").fill("2030")

	page.get_by_role("button", name="Pay and Confirm Order").click()

	#  Assert order success and download invoice
	expect(page.get_by_text("Order Placed!")).to_be_visible()
	with page.expect_download() as download_info:
		page.get_by_text("Download Invoice").click()
	download = download_info.value
	download_path = Path(r"D:\Downloads\\invoice.txt")
	download.save_as(str(download_path))
	assert download_path.exists()


def test_add_to_cart(page: Page):
	# Log in as agent01
	page.goto("https://automationexercise.com/", wait_until="domcontentloaded")
	page.get_by_text("Signup / Login").click()
	page.wait_for_url("**/login")
	page.locator("[data-qa='login-email']").fill("agent01@qq.com")
	page.locator("[data-qa='login-password']").fill("123456")
	page.get_by_role("button", name="Login").click()

	# Go to Products (All Products)
	page.get_by_role("link", name="Products").click()
	expect(page).to_have_url(re.compile(r".*/products"))

	# Select two specific products via overlay: Men Tshirt, Stylish Dress
	products_to_add = ["Men Tshirt", "Stylish Dress"]
	for idx, name in enumerate(products_to_add):
		product = page.locator(".single-products").filter(
			has=page.get_by_text(name)
		)
		product.hover()
		product.locator(".product-overlay .add-to-cart").click()
		expect(page.get_by_text("Added!")).to_be_visible()
		if idx == 0:
			page.get_by_text("Continue Shopping").click()
			expect(page).to_have_url(re.compile(r".*/products"))
		else:
			page.get_by_text("View Cart").click()
			expect(page).to_have_url(re.compile(r".*/view_cart"))

	# Proceed to checkout and place order (reuse same flow)
	page.get_by_text("Proceed To Checkout").first.click()
	expect(page).to_have_url(re.compile(r".*/checkout"))
	page.get_by_role("link", name="Place Order").click()
	expect(page).to_have_url(re.compile(r".*/payment"))

	# Fill payment form using data-qa selectors (hyphenated names)
	page.locator("[data-qa='name-on-card']").fill("funx")
	page.locator("[data-qa='card-number']").fill("12345678")
	page.locator("[data-qa='cvc']").fill("311")
	page.locator("[data-qa='expiry-month']").fill("06")
	page.locator("[data-qa='expiry-year']").fill("2030")

	page.get_by_role("button", name="Pay and Confirm Order").click()

	# Assert order success and download invoice
	expect(page.get_by_text("Order Placed!")).to_be_visible()
	with page.expect_download() as download_info:
		page.get_by_text("Download Invoice").click()
	download = download_info.value
	download_path = Path(r"D:\Downloads\\invoice.txt")
	download.save_as(str(download_path))
	assert download_path.exists()
	






