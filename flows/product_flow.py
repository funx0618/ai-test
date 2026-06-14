"""
ProductFlow - 产品 & 购物车 & 结算的复合业务流程

作用：
  - 将「搜索商品 → 查看详情 → 加入购物车 → 结算 → 支付」
    这个多步骤操作封装成一个方法
  - 测试用例只需一行调用即可完成复杂业务流程

"""

import re

from playwright.sync_api import Page, expect
from pages.product_page import ProductPage


class ProductFlow:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.product_page = ProductPage(page)

    # ========== 产品浏览 ==========
    def open_products(self) -> None:
        """从首页进入产品列表页"""
        self.product_page.open_via_homepage()

    def search_product(self, keyword: str) -> None:
        """打开产品页并搜索商品"""
        self.open_products()
        self.product_page.search(keyword)

    def search_and_view_product(self, keyword: str) -> None:
        """搜索商品并查看第一个结果的详情"""
        self.search_product(keyword)
        self.product_page.view_product(keyword)

    # ========== 加入购物车 ==========
    def add_product_to_cart(self, name: str, continue_shopping: bool = True) -> None:
        """从产品列表页搜索并添加商品到购物车"""
        self.search_product(name)
        self.product_page.add_to_cart_from_listing(name, continue_shopping)

    def add_product_to_cart_from_listing(self, name: str, continue_shopping: bool = True) -> None:
        """从产品列表页直接添加商品到购物车（不搜索，适用于已在产品页的场景）"""
        self.product_page.add_to_cart_from_listing(name, continue_shopping)

    # ========== 购物车验证 ==========
    def verify_product_in_cart(self, product_name: str) -> None:
        """验证商品在购物车中"""
        self.product_page.expect_product_in_cart(product_name)

    def verify_product_not_in_cart(self, product_name: str) -> None:
        """验证商品不在购物车中"""
        self.product_page.expect_product_not_in_cart(product_name)

    def verify_cart_price(self, product_name: str, expected_quantity: int = 1) -> None:
        """验证购物车中商品的 price * quantity = total"""
        price = self.product_page.get_cart_price(product_name)
        quantity = self.product_page.get_cart_quantity(product_name)
        total = self.product_page.get_cart_total(product_name)
        assert quantity == expected_quantity, f"Expected quantity {expected_quantity}, got {quantity}"
        assert total == price * quantity, f"Expected {price * quantity}, got {total}"

    def verify_checkout_total_amount(self, *product_names: str) -> None:
        """验证 checkout 页面的 Total Amount 等于各商品 cart total 之和"""
        expected = sum(self.product_page.get_cart_total(name) for name in product_names)
        self.product_page.expect_checkout_total_amount(expected)

    # ========== 删除商品 ==========
    def remove_product_from_cart(self, product_name: str) -> None:
        """从购物车删除商品并验证已删除"""
        self.product_page.delete_from_cart(product_name)
        self.product_page.expect_product_not_in_cart(product_name)

    def clear_cart(self) -> None:
        """打开购物车并清空所有商品"""
        self.product_page.open_cart()
        self.product_page.clear_cart()

    # ========== 结算流程 ==========
    def checkout_and_pay(
        self,
        name: str = "funx",
        card_number: str = "12345678",
        cvc: str = "311",
        expiry_month: str = "06",
        expiry_year: str = "2030",
        download_invoice: bool = False,
        expected_total_amount: int | None = None,
    ) -> None:
        """完整结算流程：进入购物车 → 结算 → 验证金额 → 支付 → 验证下单成功"""
        if not re.search(r"/view_cart", self.page.url):
            self.product_page.view_cart()
        self.product_page.proceed_to_checkout()
        if expected_total_amount is not None:
            self.product_page.expect_checkout_total_amount(expected_total_amount)
        self.product_page.place_order()
        self.product_page.fill_payment(
            name=name,
            card_number=card_number,
            cvc=cvc,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
        )
        self.product_page.pay_and_confirm()
        self.product_page.expect_order_placed()

        if download_invoice:
            self.product_page.download_invoice()

    def verify_order_placed(self) -> None:
        """验证下单成功"""
        self.product_page.expect_order_placed()
