"""Fixtures compartidas: driver de Chrome y captura automatica si un test falla."""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.screenshots import take_screenshot


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def driver(request):
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.page_load_strategy = "eager"  # no espera a los anuncios externos
    if os.getenv("HEADLESS", "0") == "1":
        options.add_argument("--headless=new")

    # Selenium Manager descarga/gestiona el chromedriver automaticamente.
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(0)  # solo esperas explicitas (WebDriverWait)
    yield drv

    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        take_screenshot(drv, f"FALLO_{request.node.name}")
    drv.quit()
