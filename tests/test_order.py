"""
test_order.py - 产品 & 订单相关测试

使用 ProductFlow + ProductPage 进行产品操作和验证
"""

from flows.product_flow import ProductFlow


def test_product_search(page):
    """搜索商品 Stylish Dress 并验证查询结果"""
    product_flow = ProductFlow(page)

    # Step 1: 搜索商品
    product_flow.search_product("Stylish Dress")

    # Step 2: 验证搜索结果中包含 Stylish Dress
    product_flow.product_page.expect_product_in_search_results("Stylish Dress")


def test_check_out(logged_in_page):
    """添加两件商品到购物车，结算并验证价格，下载小票"""
    page = logged_in_page
    product_flow = ProductFlow(page)

    # Step 0: 清空购物车（避免之前测试遗留的商品影响）
    product_flow.clear_cart()

    # Step 1: 搜索并添加 Stylish Dress（1件，留在产品页继续选）
    product_flow.add_product_to_cart("Stylish Dress", continue_shopping=True)

    # Step 2: 搜索并添加 Sleeves Top and Short - Blue & Pink（1件，弹窗保持可见）
    product_flow.add_product_to_cart("Sleeves Top and Short - Blue & Pink", continue_shopping=False)

    # Step 3: 从弹窗点击 View Cart 进入购物车
    product_flow.product_page.view_cart()

    # Step 4: 验证购物车中两件商品的价格
    product_flow.verify_cart_price("Stylish Dress", expected_quantity=1)
    product_flow.verify_cart_price("Sleeves Top and Short - Blue & Pink", expected_quantity=1)

    # Step 5: 下单并支付（含 Total Amount 验证），下载小票
    stylish_total = product_flow.product_page.get_cart_row_total("Stylish Dress")
    sleeves_total = product_flow.product_page.get_cart_row_total("Sleeves Top and Short - Blue & Pink")
    expected_total = stylish_total + sleeves_total
    product_flow.checkout_and_pay(download_invoice=True, expected_total_amount=expected_total)


def test_product_detail_review_and_add_to_cart(logged_in_page, default_user):
    """商品详情页：调整数量、提交评论、加入购物车并验证"""
    page = logged_in_page
    product_flow = ProductFlow(page)

    # Step 0: 清空购物车
    product_flow.clear_cart()

    # Step 1: 进入产品列表，点击第一个商品的 View Product 进入详情页
    product_flow.open_products()
    product_flow.product_page.view_product_first()
    product_name = product_flow.product_page.get_product_detail_name()

    # Step 2: 数量上2次下1次 → 变为2
    product_flow.product_page.set_quantity_with_arrows(up_clicks=2, down_clicks=1)
    assert product_flow.product_page.get_quantity() == 2

    # Step 3: 提交评论
    product_flow.product_page.submit_review(
        name=default_user["username"],
        email=default_user["email"],
        review="Great product! Good quality and fast delivery.",
    )
    product_flow.product_page.expect_review_submitted()

    # Step 4: 加入购物车，验证数量和商品名称
    product_flow.product_page.add_to_cart_from_detail()
    product_flow.product_page.view_cart()
    product_flow.verify_product_in_cart(product_name)
    assert product_flow.product_page.get_cart_quantity(product_name) == 2

