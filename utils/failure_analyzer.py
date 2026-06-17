"""
failure_analyzer.py - Failure Analysis Data & Utilities

Purpose:
  - Define FailureReport data structure
  - Capture DOM snapshot from Playwright page
  - Format and save analysis reports to reports/ directory

Analysis is performed by the AI Agent (ai/agent.py).
"""

import re
import os
from datetime import datetime
from dataclasses import dataclass, field


# ========== Project paths ==========
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(_PROJECT_ROOT, "reports")


@dataclass
class FailureReport:
    """Structured failure analysis report."""
    test_name: str = ""
    failure_type: str = ""
    root_cause: str = ""
    error_message: str = ""
    dom_snapshot: str = ""
    stack_trace: str = ""
    network_logs: str = ""
    evidence: list = field(default_factory=list)
    suggested_fix: list = field(default_factory=list)
    confidence: float = 0.00


# =====================================================================
#  DOM Capture
'''
capture_dom_snapshot 在 conftest.py 的 pytest_runtest_makereport hook 中被调用，
此时测试刚失败、页面还没关闭，所以能拿到失败瞬间的 DOM 状态
参数解释：
re.DOTALL ： 让 . 匹配包括换行符在内的所有字符（默认 . 不匹配 \n）
re.IGNORECASE ： 不区分大小写，匹配 <BODY>、<Body>` 等变体
'''
# =====================================================================

def capture_dom_snapshot(page_obj, max_length: int = 2000) -> str:
    """Capture a DOM snapshot from the page (body content, truncated)."""
    try:
        html = page_obj.content()
        body_match = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
        if body_match:
            snippet = body_match.group(1).strip()[:max_length]
        else:
            snippet = html[:max_length]
        return snippet
    except Exception:
        return "<DOM capture failed>"


# =====================================================================
#  Report Formatting & Output
# =====================================================================

def format_report(report: FailureReport) -> str:
    """Format FailureReport into the required text output format."""
    lines = [
        "Test Name:",
        report.test_name,
        "",
        "Failure Type:",
        report.failure_type,
        "",
        "Root Cause:",
        report.root_cause,
        "",
        "Error:",
        report.error_message,
        "",
        "Evidence:",
    ]
    for ev in report.evidence:
        lines.append(f"- {ev}")

    lines.append("")
    lines.append("Suggested Fix:")
    for fix in report.suggested_fix:
        lines.append(fix)

    lines.append("")
    lines.append("Confidence Score:")
    lines.append(f"{report.confidence:.2f}")

    return "\n".join(lines)


def save_report(report: FailureReport) -> str:
    """
    Save the failure analysis report to reports/ directory.

    Returns:
        Path to the saved report file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = report.test_name.replace("/", "_").replace("::", "_").replace(":", "")
    filename = f"failure_analysis_{safe_name}_{ts}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    content = format_report(report)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
