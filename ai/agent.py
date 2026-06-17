"""
ai/agent.py - AI Agent Failure Analyzer

使用 LLM 对测试失败进行智能分析。

支持的 LLM 后端：
  - Xiaomi MiMo (mimo-v2.5-pro) ← 当前默认
  - OpenAI (GPT-4o, GPT-4, etc.)

工作流程：
  1. 收集上下文（错误信息、DOM、堆栈、测试源码）
  2. 构建结构化 prompt
  3. 调用 LLM 获取分析结果
  4. 解析 LLM 响应为 FailureReport

使用方式：
  from ai.agent import analyze_with_ai
  report = analyze_with_ai(test_name, error_message, page_obj)
"""

import re
import os
from typing import Optional

from ai.config import (
    LLM_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL,
    MIMO_API_KEY, MIMO_MODEL, MIMO_BASE_URL,
    LLM_TIMEOUT, MAX_TOKENS, TEMPERATURE,
)
from utils.failure_analyzer import (
    FailureReport,
    capture_dom_snapshot,
)

# =====================================================================
#  Prompt Template
# =====================================================================

SYSTEM_PROMPT = """You are an expert test automation failure analyst.
You analyze Playwright + pytest test failures and provide structured diagnosis.

You MUST respond in EXACTLY this format (plain text, no markdown):

Root Cause:
<one-line root cause>

Failure Type:
<Locator Failure | Assertion Failure | Network Failure | Data Failure | Environment Failure>

Evidence:
- <evidence point 1>
- <evidence point 2>
- ...

Suggested Fix:
# Fix 1: <brief description>
# Before:
<original broken code>
# After:
<corrected code>

# Fix 2: <brief description>
# Before:
<original broken code>
# After:
<corrected code>

Confidence Score:
<0.00 to 1.00>

Rules:
- Be specific and actionable
- Base evidence on the actual error message and DOM
- Suggested Fix MUST be actual Python/Playwright code, NOT text descriptions
- Show before/after code when possible
- Use comments (#) to explain the fix
- Confidence reflects how certain you are (0.90+ = high, 0.70-0.89 = medium, <0.70 = low)
"""

USER_PROMPT_TEMPLATE = """Analyze this test failure:

## Test Name
{test_name}

## Error Message
{error_message}

## Stack Trace
{stack_trace}

## Page DOM Snapshot (truncated)
{dom_snapshot}

## Test Source Code
{test_source}

Provide your analysis in the exact format specified."""


# =====================================================================
#  LLM Client
# =====================================================================

def _get_openai_client():
    """Create an OpenAI-compatible client based on provider config."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "openai package not installed. Run: pip install openai"
        )

    if LLM_PROVIDER == "mimo":
        return OpenAI(
            api_key=MIMO_API_KEY,
            base_url=MIMO_BASE_URL,
            timeout=LLM_TIMEOUT,
        )
    else:  # openai
        return OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            timeout=LLM_TIMEOUT,
        )


def _get_model_name() -> str:
    """Return the model name for the current provider."""
    if LLM_PROVIDER == "mimo":
        return MIMO_MODEL
    return OPENAI_MODEL


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call LLM and return the response text."""
    client = _get_openai_client()
    model = _get_model_name()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    return response.choices[0].message.content.strip()


# =====================================================================
#  Response Parser
# =====================================================================

def _parse_llm_response(response: str) -> dict:
    """Parse the structured LLM response into a dict."""
    result = {
        "root_cause": "Unknown Root Cause",
        "failure_type": "Environment Failure",
        "evidence": [],
        "suggested_fix": [],
        "confidence": 0.50,
    }

    # Extract Root Cause
    rc_match = re.search(r"Root Cause:\s*\n(.+?)(?:\n\n|\nFailure Type:)", response, re.DOTALL)
    if rc_match:
        result["root_cause"] = rc_match.group(1).strip()

    # Extract Failure Type
    ft_match = re.search(r"Failure Type:\s*\n(.+?)(?:\n\n|\nEvidence:)", response, re.DOTALL)
    if ft_match:
        result["failure_type"] = ft_match.group(1).strip()

    # Extract Evidence
    ev_match = re.search(r"Evidence:\s*\n(.+?)(?:\n\n|\nSuggested Fix:)", response, re.DOTALL)
    if ev_match:
        lines = ev_match.group(1).strip().split("\n")
        result["evidence"] = [
            line.lstrip("- ").strip()
            for line in lines if line.strip().startswith("-")
        ]

    # Extract Suggested Fix (capture all lines including code)
    sf_match = re.search(r"Suggested Fix:\s*\n(.+?)(?:\n\n|\nConfidence Score:)", response, re.DOTALL)
    if sf_match:
        fix_text = sf_match.group(1).strip()
        # Split by empty lines to get separate fix blocks
        result["suggested_fix"] = [fix_text]

    # Extract Confidence Score
    cs_match = re.search(r"Confidence Score:\s*\n?([\d.]+)", response)
    if cs_match:
        try:
            score = float(cs_match.group(1))
            result["confidence"] = max(0.0, min(1.0, score))
        except ValueError:
            pass

    return result


# =====================================================================
#  Test Source Extraction
# =====================================================================

def _get_test_source(test_name: str) -> str:
    """Try to read the test source code for additional context."""
    test_files = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", f)
        for f in ["test_login.py", "test_order.py", "test_login_flow.py",
                   "test_non_business.py", "test_order_flow.py", "test_playwright.py"]
    ]
    for filepath in test_files:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # Find the test function
            pattern = rf"(def {test_name}\b.*?)(?=\ndef |\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()[:3000]  # Limit to 3000 chars
        except Exception:
            continue
    return "<source code not found>"


# =====================================================================
#  Main Entry Point
# =====================================================================

def analyze_with_ai(
    test_name: str,
    error_message: str,
    page_obj=None,
    stack_trace: str = "",
) -> FailureReport:
    """
    AI-powered failure analysis using LLM.

    Flow:
      1. Collect context (error, DOM, test source)
      2. Call LLM for analysis
      3. Parse response into FailureReport
      4. If LLM fails → return a minimal report

    Args:
        test_name: Name of the failed test
        error_message: The error/exception message
        page_obj: Playwright page object (for DOM capture)
        stack_trace: Full stack trace

    Returns:
        FailureReport with all analysis fields populated
    """
    dom_snapshot = ""
    if page_obj:
        dom_snapshot = capture_dom_snapshot(page_obj)

    test_source = _get_test_source(test_name)

    try:
        user_prompt = USER_PROMPT_TEMPLATE.format(
            test_name=test_name,
            error_message=error_message,
            stack_trace=stack_trace or "<not provided>",
            dom_snapshot=dom_snapshot[:2000] or "<not available>",
            test_source=test_source[:3000],
        )

        llm_response = _call_llm(SYSTEM_PROMPT, user_prompt)
        parsed = _parse_llm_response(llm_response)

        return FailureReport(
            test_name=test_name,
            failure_type=parsed["failure_type"],
            root_cause=parsed["root_cause"],
            error_message=error_message,
            dom_snapshot=dom_snapshot,
            stack_trace=stack_trace,
            evidence=parsed["evidence"],
            suggested_fix=parsed["suggested_fix"],
            confidence=parsed["confidence"],
        )

    except Exception as llm_error:
        print(f"⚠️  AI Agent failed ({type(llm_error).__name__}: {llm_error})")
        return FailureReport(
            test_name=test_name,
            failure_type="Unknown",
            root_cause="AI Analysis Failed",
            error_message=error_message,
            stack_trace=stack_trace,
            evidence=[f"AI Agent error: {type(llm_error).__name__}"],
            suggested_fix=["Manual investigation required"],
            confidence=0.00,
        )
