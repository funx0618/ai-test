"""
test_order.py - 产品 & 订单相关测试

使用 ProductFlow + ProductPage 进行产品操作和验证
"""

from flows.product_flow import ProductFlow
from flows.login_flow import LoginFlow


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


def test_remove_product_from_cart(logged_in_page):
    """从购物车中删除商品并验证"""
    page = logged_in_page
    product_flow = ProductFlow(page)

    # Step 0: 清空购物车
    product_flow.clear_cart()

    # Step 1: 添加两件商品到购物车
    product_flow.add_product_to_cart("Stylish Dress", continue_shopping=True)
    product_flow.add_product_to_cart("Sleeves Top and Short - Blue & Pink", continue_shopping=False)
    product_flow.product_page.view_cart()

    # Step 2: 验证两件商品都在购物车中
    product_flow.verify_product_in_cart("Stylish Dress")
    product_flow.verify_product_in_cart("Sleeves Top and Short - Blue & Pink")

    # Step 3: 删除 Stylish Dress
    product_flow.remove_product_from_cart("Stylish Dress")

    # Step 4: 验证 Stylish Dress 已删除，另一件仍存在
    product_flow.verify_product_not_in_cart("Stylish Dress")
    product_flow.verify_product_in_cart("Sleeves Top and Short - Blue & Pink")


def test_brands_count(page):
    """验证品牌侧边栏显示的数量与品牌页面实际商品数一致"""
    product_flow = ProductFlow(page)

    # Step 1: 进入产品页（品牌侧边栏在产品页可见）
    product_flow.open_products()

    # Step 2: 验证每个品牌的数量
    product_flow.verify_brands_product_count()


def test_category(page):
    """遍历所有分类并验证页面标题正确"""
    product_flow = ProductFlow(page)

    # 验证所有分类页面标题
    product_flow.verify_categories()


def test_login_while_checkout(page, default_user):
    """不登录状态下添加商品，结算时触发登录，完成下单"""
    product_flow = ProductFlow(page)
    login_flow = LoginFlow(page)

    # Step 1: 不登录，直接进入产品页搜索并添加商品到购物车
    product_flow.add_product_to_cart("Fancy Green Top", continue_shopping=False)

    # Step 2: 从弹窗点击 View Cart 进入购物车
    product_flow.product_page.view_cart()

    # Step 3: 点击 Proceed To Checkout，弹出登录弹窗
    product_flow.product_page.click_proceed_to_checkout()
    # 此时应弹出 modal 要求登录
    product_flow.product_page.click_register_login_from_modal()

    # Step 4: 登录
    login_flow.login_page.login(default_user["email"], default_user["password"])
    login_flow.login_page.expect_logged_in(default_user["username"])

    # Step 5: 登录后返回购物车
    product_flow.product_page.go_to_cart()

    # Step 6: 再次结算并支付
    product_flow.checkout_and_pay()


def test_register_while_checkout(page):
    """不登录状态下添加商品，结算时注册新用户，登录后进入购物车完成下单"""
    product_flow = ProductFlow(page)
    login_flow = LoginFlow(page)

    # Step 1: 不登录，搜索并添加商品到购物车
    product_flow.add_product_to_cart("Fancy Green Top", continue_shopping=False)

    # Step 2: 从弹窗点击 View Cart 进入购物车
    product_flow.product_page.view_cart()

    # Step 3: 点击 Proceed To Checkout，弹出登录/注册弹窗
    product_flow.product_page.click_proceed_to_checkout()
    product_flow.product_page.click_register_login_from_modal()

    # Step 4: 注册新用户（注册后自动登录）
    login_flow.signup(name="checkout_user", email="checkout_user@test.com")
    login_flow.verify_register_success()

    # Step 5: 点击 Continue 进入首页
    login_flow.login_page.continue_after_register()

    # Step 6: 点击 Cart 进入购物车
    product_flow.product_page.go_to_cart()

    # Step 7: 结算并支付
    product_flow.checkout_and_pay()

    # Step 8: 清理 — 删除注册的账户
    login_flow.delete_account()

