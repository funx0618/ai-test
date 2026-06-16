"""
test_order.py - 产品 & 订单相关测试

使用 ProductFlow + ProductPage 进行产品操作和验证

测试数据：从 data/test_products.json 加载
"""

from flows.product_flow import ProductFlow
from flows.login_flow import LoginFlow
from utils.data_loader import load_test_products, load_test_users, generate_random_user

PRODUCTS = load_test_products()
USERS = load_test_users()


def test_product_search(page):
    """搜索商品并验证查询结果"""
    product_flow = ProductFlow(page)
    keyword = PRODUCTS["product_search"]

    # Step 1: 搜索商品
    product_flow.search_product(keyword)

    # Step 2: 验证搜索结果中包含该商品
    product_flow.product_page.expect_product_in_search_results(keyword)


def test_check_out(logged_in_page):
    """添加两件商品到购物车，结算并验证价格，下载小票"""
    page = logged_in_page
    product_flow = ProductFlow(page)
    checkout_items = PRODUCTS["check_out"]

    # Step 0: 清空购物车（避免之前测试遗留的商品影响）
    product_flow.clear_cart()

    # Step 1 & 2: 依次搜索并添加商品到购物车
    for item in checkout_items:
        product_flow.add_product_to_cart(item["name"], continue_shopping=item["continue_shopping"])

    # Step 3: 从弹窗点击 View Cart 进入购物车
    product_flow.product_page.view_cart()

    # Step 4: 验证购物车中每件商品的价格
    for item in checkout_items:
        product_flow.verify_cart_price(item["name"], expected_quantity=1)

    # Step 5: 下单并支付（含 Total Amount 验证），下载小票
    expected_total = sum(
        product_flow.product_page.get_cart_row_total(item["name"]) for item in checkout_items
    )
    product_flow.checkout_and_pay(download_invoice=True, expected_total_amount=expected_total)

    # Step 6: 点击 Continue 返回首页
    product_flow.product_page.continue_after_order()


def test_empty_cart(logged_in_page):
    """验证空购物车逻辑：清空购物车后点击 here 链接进入产品页"""
    page = logged_in_page
    product_flow = ProductFlow(page)

    # Step 1: 点击导航栏 Cart 按钮进入购物车
    product_flow.product_page.go_to_cart()

    # Step 2: 如果购物车中有商品，则清空
    if product_flow.product_page.is_cart_has_items():
        product_flow.product_page.clear_cart()

    # Step 3: 点击 here 链接进入产品页
    product_flow.product_page.click_here_to_products()

    # Step 4: 验证已跳转到产品页
    product_flow.product_page.expect_on_products_page()


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
    remove_items = PRODUCTS["remove_product_from_cart"]

    # Step 0: 清空购物车
    product_flow.clear_cart()

    # Step 1: 添加两件商品到购物车
    for item in remove_items:
        product_flow.add_product_to_cart(item["name"], continue_shopping=item["continue_shopping"])
    product_flow.product_page.view_cart()

    # Step 2: 验证两件商品都在购物车中
    for item in remove_items:
        product_flow.verify_product_in_cart(item["name"])

    # Step 3: 删除第一件商品
    product_flow.remove_product_from_cart(remove_items[0]["name"])

    # Step 4: 验证第一件已删除，其余仍存在
    product_flow.verify_product_not_in_cart(remove_items[0]["name"])
    product_flow.verify_product_in_cart(remove_items[1]["name"])


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
    checkout_product = PRODUCTS["login_while_checkout"]

    # Step 1: 不登录，直接进入产品页搜索并添加商品到购物车
    product_flow.add_product_to_cart(checkout_product["name"], continue_shopping=checkout_product["continue_shopping"])

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
    checkout_product = PRODUCTS["register_while_checkout"]
    user = generate_random_user()

    # Step 1: 不登录，搜索并添加商品到购物车
    product_flow.add_product_to_cart(checkout_product["name"], continue_shopping=checkout_product["continue_shopping"])

    # Step 2: 从弹窗点击 View Cart 进入购物车
    product_flow.product_page.view_cart()

    # Step 3: 点击 Proceed To Checkout，弹出登录/注册弹窗
    product_flow.product_page.click_proceed_to_checkout()
    product_flow.product_page.click_register_login_from_modal()

    # Step 4: 注册新用户（注册后自动登录）
    login_flow.signup(name=user["name"], email=user["email"])
    login_flow.verify_register_success()

    # Step 5: 点击 Continue 进入首页
    login_flow.login_page.continue_after_register()

    # Step 6: 点击 Cart 进入购物车
    product_flow.product_page.go_to_cart()

    # Step 7: 结算并支付
    product_flow.checkout_and_pay()

    # Step 8: 清理 — 删除注册的账户
    login_flow.delete_account()


def test_product_subscription(page):
    """在产品列表页滚动到底部，填写邮箱并订阅，验证成功提示"""
    product_flow = ProductFlow(page)
    login_flow = LoginFlow(page)
    user = USERS["login"]

    # Step 1: 登录
    login_flow.login_as(
        email=user["email"],
        password=user["password"],
    )
    login_flow.verify_login(username=user["username"])

    # Step 2: 进入产品列表页，滚动到底部并订阅
    product_flow.subscribe_on_products_page(email=user["email"])

