import pytest
import allure
import logging
from pathlib import Path
from playwright.sync_api import Page, expect

from page_registry import PageRegistry
from utilities.load_json_test_data import read_json

# Set global assertion timeout to 20 seconds (20000 ms) as Orange HRM site is slow often times
expect.set_options(timeout=20000)

@pytest.fixture(scope="session")
def test_data():
    return read_json("test_data.json")

@pytest.fixture(scope="function")
def pages(page: Page, request):
    return PageRegistry(page, request)

@pytest.fixture(scope="function")
def scenario_context():
    """Dictionary to share state between BDD steps in a scenario."""
    return {}

@pytest.fixture(autouse=True)
def _multi_browser(browser_name):
    """Forces pytest-playwright to parametrize tests across --browser values,
    which otherwise breaks when a custom fixture wraps `page` (see
    microsoft/playwright-pytest#172). so explicitly pulling in the browser_name fixture"""
    return browser_name

@pytest.hookimpl(hookwrapper=True)
def pytest_bdd_before_scenario(request, feature, scenario):
    yield
    browser = request.getfixturevalue("browser_name")
    allure.dynamic.tag(browser)
    allure.dynamic.parameter("browser", browser)

    # Pull out any Examples-table values pytest-bdd parametrized this scenario with
    callspec = getattr(request.node, "callspec", None)
    example_params = {}
    if callspec:
        example_params = {k: v for k, v in callspec.params.items() if k != "browser_name"}

    for name, value in example_params.items():
        allure.dynamic.parameter(name, value)

    if example_params:
        example_suffix = ", ".join(f"{k}={v}" for k, v in example_params.items())
        allure.dynamic.title(f"{scenario.name} [{example_suffix}] [{browser}]")
    else:
        allure.dynamic.title(f"{scenario.name} [{browser}]")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    yield
    try:
        # 1. Resolve base test-results directory
        base_dir = item.config.getoption("--output", default="test-results")
        base_path = Path(base_dir)
        if not base_path.is_dir():
            return
        # 2. Find the node id slug
        node_id_slug = item.name.replace("_", "-").replace("@","-").replace(" ","-").replace("[", "-").replace("]","").replace("...", "-").replace(".", "-").replace("---", "-").replace("--", "-").lower()

        # 3. Find the specific subdirectory matching this unique slug string
        specific_test_dir = None
        for folder in base_path.iterdir():
            if folder.is_dir() and node_id_slug in folder.name:
                specific_test_dir = folder
                break

        # 4. Process and attach media ONLY from this target subdirectory
        if specific_test_dir:
            for file in specific_test_dir.iterdir():
                if file.is_file():
                    logging.info(f"Attaching file: {file.name} to {item.name}")

                    if file.suffix == ".png":
                        allure.attach.file(
                            str(file),
                            name=file.name,
                            attachment_type=allure.attachment_type.PNG,
                        )
                    elif file.suffix == ".webm":
                        allure.attach.file(
                            str(file),
                            name=file.name,
                            attachment_type=allure.attachment_type.WEBM,
                        )
    except Exception as e:
        logging.error(f"Error attaching localized test screenshot/video: {e}")