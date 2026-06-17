"""
Root conftest.py - 注册 fixtures & 测试生命周期 hook

作用：
  1. 导入 fixtures/ 中的 fixture，让 pytest 自动发现
  2. 测试失败时自动运行 AI Failure Analysis 并输出报告
"""

import traceback

import pytest

# 导入自定义 fixtures，让 pytest 自动发现
from fixtures.browser_fixture import browser, context, page
from fixtures.user_fixture import default_user, login_page, login_flow, logged_in_page
from ai.agent import analyze_with_ai
from utils.failure_analyzer import format_report, save_report


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动保存 trace、screenshot 并运行 AI Failure Analysis。"""
    outcome = yield
    report = outcome.get_result()

    # 只在 call 阶段（测试执行阶段）且失败时处理
    if report.when != "call" or report.passed:
        return

    # 获取 page fixture
    page_obj = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
    if not page_obj:
        return

    # ===== AI Failure Analysis =====
    # 提取错误信息
    exc_info = call.excinfo
    if exc_info is not None:
        error_lines = traceback.format_exception_only(exc_info.type, exc_info.value)
        error_message = "".join(error_lines).strip()
    else:
        error_message = str(report.longrepr) if report.longrepr else "Unknown error"

    test_name = item.nodeid.split("::")[-1]

    # 运行 AI Agent 分析
    analysis = analyze_with_ai(
        test_name=test_name,
        error_message=error_message,
        page_obj=page_obj,
        stack_trace="".join(traceback.format_exception(call.excinfo.type, call.excinfo.value, call.excinfo.tb)) if call.excinfo else "",
    )

    # 保存报告到 reports/ 目录
    report_path = save_report(analysis)

    # 输出报告到终端
    print("\n" + format_report(analysis))
    print(f"\n📄 Failure analysis report saved to: {report_path}")
