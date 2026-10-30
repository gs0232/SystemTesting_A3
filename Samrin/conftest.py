"""Shared browser setup and evidence capture; no real personal data is used."""
import csv
import os
from datetime import datetime, timezone
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

BASE = 'https://opencart.abstracta.us/'
OUT = Path('results') / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
OUT.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def page(request):
    # Each scenario receives a clean browser context, avoiding state leakage.
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.getenv('HEADED') != '1')
        context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        page = context.new_page()
        page.set_default_timeout(20000)
        request.node.browser_page = page
        yield page
        context.close()
        browser.close()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != 'call':
        return
    name = item.nodeid.replace('/', '_').replace('::', '_')
    page = getattr(item, 'browser_page', None)
    shot = OUT / (name + '.png')
    if page and not page.is_closed():
        page.screenshot(path=str(shot), full_page=True)
    # A rejected invalid input is PASS when the expected warning is asserted.
    status = 'BLOCKED' if report.skipped else ('PASS' if report.passed else
             ('FAIL' if isinstance(call.excinfo.value, AssertionError) else 'ERROR'))
    path = OUT / 'results.csv'
    new = not path.exists()
    with path.open('a', newline='') as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(['scenario', 'status', 'detail', 'screenshot'])
        writer.writerow([item.nodeid, status, '' if report.passed else report.longreprtext,
                         str(shot) if shot.exists() else ''])
