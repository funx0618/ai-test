"""
Root conftest.py - 注册 fixtures & 测试生命周期 hook

作用：
  1. 导入 fixtures/ 中的 fixture，让 pytest 自动发现
  2. 测试失败时自动保存 trace.zip 和 screenshot
"""

import os
from datetime import datetime

import pytest

# 导入自定义 fixtures，让 pytest 自动发现
from fixtures.browser_fixture import browser, context, page, _ensure_output_dirs
from fixtures.user_fixture import default_user, login_page, login_flow, logged_in_page

# 项目根目录
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TRACES_DIR = os.path.join(_PROJECT_ROOT, "traces")
SCREENSHOTS_DIR = os.path.join(_PROJECT_ROOT, "screenshots")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动保存 trace 和 screenshot。"""
    outcome = yield
    report = outcome.get_result()

    # 只在 call 阶段（测试执行阶段）且失败时处理
    if report.when != "call" or report.passed:
        return

    # 获取 page fixture
    page_obj = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
    if not page_obj:
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = item.nodeid.replace("/", "_").replace("::", "_").replace(":", "")

    # 保存 screenshot
    try:
        ss_path = os.path.join(SCREENSHOTS_DIR, f"{safe_name}_{ts}.png")
        page_obj.screenshot(path=ss_path, full_page=True)
    except Exception:
        pass

    # 保存 trace
    try:
        trace_path = os.path.join(TRACES_DIR, f"{safe_name}_{ts}.zip")
        page_obj.context.tracing.stop(path=trace_path)
    except Exception:
        pass
