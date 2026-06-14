"""
ProductPage - 产品 & 购物车 & 结算页面对象，只负责页面交互，不负责业务流程

作用：
  - 封装 automationexercise.com 的产品相关页面所有交互
  - 包括：产品列表、搜索、商品详情、加入购物车、购物车操作、结算、支付

"""

import re
from pathlib import Path
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class ProductPage(BasePage):
    URL = "/products"
    PAGE_NAME = "ProductPage"

    # ========== 搜索 ==========
    SEARCH_INPUT = "#search_product"
    SEARCH_BTN = "#submit_search"

    # ========== 支付表单 ==========
    NAME_ON_CARD = "[data-qa='name-on-card']"
    CARD_NUMBER = "[data-qa='card-number']"
    CVC = "[data-qa='cvc']"
    EXPIRY_MONTH = "[data-qa='expiry-month']"
    EXPIRY_YEAR = "[data-qa='expiry-year']"

    # ========== 导航 ==========
    def open(self) -> None:
        """直接打开产品列表页"""
        self.page.goto(f"{self.BASE_URL}{self.URL}", wait_until="domcontentloaded")

    def open_via_homepage(self) -> None:
        """从首页点击 Products 进入产品列表页"""
        self.page.goto(f"{self.BASE_URL}/", wait_until="domcontentloaded")
        self.page.get_by_role("link", name="Products").click()
        expect(self.page).to_have_url(re.compile(r".*/products"))

    # ========== 搜索 ==========
    def search(self, keyword: str) -> None:
        """搜索商品"""
        self.page.locator(self.SEARCH_INPUT).fill(keyword)
        self.page.locator(self.SEARCH_BTN).click()

    # ========== 商品操作 ==========
    def view_product(self, name: str) -> None:
        """点击指定商品的 View Product 进入详情页"""
        self.page.get_by_text("View Product").first.click()
        self.page.wait_for_url("**/product_details/*")

    def add_to_cart_from_listing(self, name: str, continue_shopping: bool = True) -> None:
        """从商品列表页通过 hover overlay 添加商品到购物车"""
        product = self.page.locator(".single-products").filter(
            has=self.page.get_by_text(name)
        ).first
        product.hover()
        product.locator(".product-overlay .add-to-cart").click()
        expect(self.page.get_by_text("Added!")).to_be_visible()

        if continue_shopping:
            self.page.get_by_text("Continue Shopping").click()
            expect(self.page).to_have_url(re.compile(r".*/products"))

    def add_to_cart_from_detail(self, quantity: int = 1) -> None:
        """从商品详情页添加到购物车"""
        if quantity > 1:
            self.page.locator("#quantity").fill(str(quantity))

        self.page.get_by_role("button", name="Add to cart").click()
        expect(self.page.get_by_text("Added!")).to_be_visible()

    # ========== 购物车 ==========
    def open_cart(self) -> None:
        """直接打开购物车页面"""
        self.page.goto(f"{self.BASE_URL}/view_cart", wait_until="domcontentloaded")

    def view_cart(self) -> None:
        """从弹窗点击 View Cart 进入购物车"""
        self.page.get_by_text("View Cart").click()
        expect(self.page).to_have_url(re.compile(r".*/view_cart"))

    def get_cart_row(self, product_name: str):
        """获取购物车中指定商品的行"""
        return self.page.locator("tr").filter(has_text=product_name)

    def expect_product_in_cart(self, product_name: str) -> None:
        """验证商品在购物车中"""
        expect(self.get_cart_row(product_name)).to_be_visible()

    def expect_product_not_in_cart(self, product_name: str) -> None:
        """验证商品不在购物车中"""
        expect(self.page.locator("tr").filter(has_text=product_name)).to_have_count(0)

    def delete_from_cart(self, product_name: str) -> None:
        """从购物车删除商品"""
        self.get_cart_row(product_name).locator(".cart_quantity_delete").click()

    def clear_cart(self) -> None:
        """清空购物车所有商品"""
        delete_buttons = self.page.locator(".cart_quantity_delete")
        while delete_buttons.count() > 0:
            delete_buttons.first.click()
            self.page.wait_for_timeout(500)

    def get_cart_price(self, product_name: str) -> int:
        """获取购物车中商品单价"""
        row = self.get_cart_row(product_name)
        price_text = row.locator(".cart_price p").inner_text()
        return int(price_text.replace("Rs. ", ""))

    def get_cart_quantity(self, product_name: str) -> int:
        """获取购物车中商品数量"""
        row = self.get_cart_row(product_name)
        return int(row.locator(".cart_quantity button").inner_text())

    def get_cart_total(self, product_name: str) -> int:
        """获取购物车中商品总价"""
        row = self.get_cart_row(product_name)
        total_text = row.locator(".cart_total p").inner_text()
        return int(total_text.replace("Rs. ", ""))

    # ========== 结算 ==========
    def proceed_to_checkout(self) -> None:
        """点击 Proceed To Checkout"""
        self.page.get_by_text("Proceed To Checkout").first.click()
        expect(self.page).to_have_url(re.compile(r".*/checkout"))

    def get_checkout_total_amount(self) -> int:
        """获取 checkout 页面的 Total Amount 金额"""
        total_row = self.page.locator("td").filter(has_text="Total Amount")
        amount_text = total_row.locator("xpath=following-sibling::td").inner_text()
        return int(amount_text.replace("Rs. ", ""))

    def expect_checkout_total_amount(self, expected_amount: int) -> None:
        """验证 checkout 页面的 Total Amount 等于预期值"""
        actual = self.get_checkout_total_amount()
        assert actual == expected_amount, (
            f"Expected Total Amount Rs. {expected_amount}, got Rs. {actual}"
        )

    def place_order(self) -> None:
        """点击 Place Order 进入支付页"""
        self.page.get_by_role("link", name="Place Order").click()
        expect(self.page).to_have_url(re.compile(r".*/payment"))

    def fill_payment(
        self,
        name: str = "funx",
        card_number: str = "12345678",
        cvc: str = "311",
        expiry_month: str = "06",
        expiry_year: str = "2030",
    ) -> None:
        """填写支付表单"""
        self.page.locator(self.NAME_ON_CARD).fill(name)
        self.page.locator(self.CARD_NUMBER).fill(card_number)
        self.page.locator(self.CVC).fill(cvc)
        self.page.locator(self.EXPIRY_MONTH).fill(expiry_month)
        self.page.locator(self.EXPIRY_YEAR).fill(expiry_year)

    def pay_and_confirm(self) -> None:
        """点击 Pay and Confirm Order"""
        self.page.get_by_role("button", name="Pay and Confirm Order").click()

    # ========== 断言 ==========
    def expect_order_placed(self) -> None:
        """验证下单成功"""
        expect(self.page.get_by_text("Order Placed!")).to_be_visible()

    def expect_product_in_search_results(self, name: str) -> None:
        """验证搜索结果中包含指定商品"""
        products = self.page.locator(".features_items .productinfo p")
        expect(products.filter(has_text=name)).to_have_count(1)

    def expect_search_results_count(self, count: int) -> None:
        """验证搜索结果数量"""
        expect(self.page.locator(".product-image-wrapper")).to_have_count(count)

    def expect_product_detail_visible(self, name: str) -> None:
        """验证商品详情页可见"""
        expect(self.page.locator(".product-information")).to_be_visible()

    def expect_checkout_modal(self) -> None:
        """验证结算弹窗可见（未登录时）"""
        expect(self.page.locator(".modal-content")).to_be_visible()

    # ========== 发票 ==========
    def download_invoice(self, save_path: str = r"D:\Downloads\\invoice.txt") -> None:
        """下载发票"""
        with self.page.expect_download() as download_info:
            self.page.get_by_text("Download Invoice").click()
        download = download_info.value
        download.save_as(save_path)
