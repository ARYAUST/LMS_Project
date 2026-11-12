"""Shared, isolated fixtures for the LMS test suite."""

from __future__ import annotations

import json
import threading
from collections.abc import Callable, Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from playwright.sync_api import APIRequestContext, Browser, Page, Playwright, sync_playwright
from werkzeug.serving import make_server

from app import create_app


ROOT = Path(__file__).parent


@pytest.fixture(scope="session")
def playwright_instance() -> Iterator[Playwright]:
    playwright = sync_playwright().start()
    yield playwright
    playwright.stop()


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Iterator[Browser]:
    browser_instance = playwright_instance.chromium.launch(headless=True)
    yield browser_instance
    browser_instance.close()


@pytest.fixture
def lms_server() -> Iterator[str]:
    with TemporaryDirectory(prefix="lms-test-") as temp_dir:
        app = create_app(str(Path(temp_dir) / "test.sqlite"))
        server = make_server("127.0.0.1", 0, app, threaded=True)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            worker.join(timeout=3)


@pytest.fixture

def base_url(lms_server: str) -> str:
    return lms_server


@pytest.fixture

def page(browser: Browser, base_url: str, request: pytest.FixtureRequest) -> Iterator[Page]:
    browser_instance = browser
    context = browser_instance.new_context(base_url=base_url)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    browser_page = context.new_page()
    request.node.ui_page = browser_page
    yield browser_page
    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        safe_name = "".join(char if char.isalnum() or char in "-_" else "_" for char in request.node.nodeid)
        screenshot_path = ROOT / "screenshots" / f"{safe_name}.png"
        trace_path = ROOT / "traces" / f"{safe_name}.zip"
        browser_page.screenshot(path=str(screenshot_path), full_page=True)
        context.tracing.stop(path=str(trace_path))
        request.node.user_properties.append(("failure screenshot", str(screenshot_path.relative_to(ROOT))))
        request.node.user_properties.append(("failure trace", str(trace_path.relative_to(ROOT))))
    else:
        context.tracing.stop()
    context.close()


@pytest.fixture
def api_context(playwright_instance: Playwright, base_url: str) -> Iterator[APIRequestContext]:
    context = playwright_instance.request.new_context(base_url=base_url, extra_http_headers={"Accept": "application/json"})
    yield context
    context.dispose()


@pytest.fixture

def api_call(api_context: APIRequestContext, record_property: Callable[[str, object], None]) -> Callable[..., object]:
    def call(method: str, path: str, **kwargs: object) -> object:
        response = getattr(api_context, method.lower())(path, **kwargs)
        try:
            body = response.text()
        except Exception:
            body = "<response body unavailable>"
        record_property(
            "API exchange",
            json.dumps({
                "method": method.upper(),
                "url": path,
                "request_data": repr(kwargs.get("data", kwargs.get("form", kwargs.get("params")))),
                "status": response.status,
                "response": body[:2000],
            }),
        )
        return response

    return call


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]) -> Iterator[None]:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
