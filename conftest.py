import pytest
import allure
import logging
from pathlib import Path
from playwright.sync_api import Page, expect

from page_registry import PageRegistry
from utilities.load_json_test_data import read_json

# OrangeHRM's demo site is slow to respond at times, so give assertions more
# room than Playwright's 5s default before failing.
expect.set_options(timeout=20000)


@pytest.fixture(scope="session")
def test_data():
    """Load shared test data (credentials, etc.) once per test session."""
    return read_json("test_data.json")


@pytest.fixture(scope="function")
def pages(page: Page, request):
    """Give each test a PageRegistry, the single entry point for all Page Objects."""
    return PageRegistry(page, request)


@pytest.fixture(scope="function")
def scenario_context():
    """Plain dict for passing state between BDD steps within one scenario."""
    return {}


@pytest.fixture(autouse=True)
def _multi_browser(browser_name):
    """Force pytest-playwright to parametrize tests across --browser values.

    Wrapping the `page` fixture (via `pages` above) otherwise breaks that
    parametrization - see microsoft/playwright-pytest#172. Requesting
    browser_name here works around it.
    """
    return browser_name


@pytest.hookimpl(hookwrapper=True)
def pytest_bdd_before_scenario(request, feature, scenario):
    """Tag each Allure scenario with its browser and Examples-table parameters."""
    yield
    browser = request.getfixturevalue("browser_name")
    allure.dynamic.tag(browser)
    allure.dynamic.parameter("browser", browser)

    # Scenario Outlines parametrize via pytest-bdd's callspec; surface those
    # values (minus browser_name, already handled above) as Allure parameters.
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
    """Attach each test's Playwright screenshot(s) and video to its Allure result."""
    yield
    try:
        base_dir = item.config.getoption("--output", default="test-results")
        base_path = Path(base_dir)
        if not base_path.is_dir():
            return

        # Playwright names each test's output folder after a slugified node ID -
        # rebuild that slug so we can find the matching folder below.
        node_id_slug = item.name.replace("_", "-").replace("@","-").replace(" ","-").replace("[", "-").replace("]","").replace("...", "-").replace(".", "-").replace("---", "-").replace("--", "-").lower()

        specific_test_dir = None
        for folder in base_path.iterdir():
            if folder.is_dir() and node_id_slug in folder.name:
                specific_test_dir = folder
                break

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