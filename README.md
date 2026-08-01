# OrangeHRM Web Automation — Playwright + Pytest-BDD

[![Build Status](https://img.shields.io/endpoint?url=https://ruby-leo.github.io/P2-HR-Management-Web-Automation-Using-Playwright-Pytest-BDD/badge.json)](https://ruby-leo.github.io/P2-HR-Management-Web-Automation-Using-Playwright-Pytest-BDD/)
[![Allure Report](https://img.shields.io/badge/Allure-Report-orange?logo=qameta)](https://ruby-leo.github.io/P2-HR-Management-Web-Automation-Using-Playwright-Pytest-BDD/)
[![Playwright](https://img.shields.io/badge/Playwright-1.61.0-2EAD33?logo=playwright)](https://playwright.dev/python/)
[![pytest-bdd](https://img.shields.io/badge/pytest--bdd-8.1.0-blue)](https://pytest-bdd.readthedocs.io/)

A BDD test automation suite for [OrangeHRM](https://opensource-demo.orangehrmlive.com), built on **Playwright + pytest-bdd** — pairing Playwright's modern, auto-waiting browser automation with Gherkin-style feature files for readable, business-facing test scenarios.

**[→ View the live Allure Report](https://ruby-leo.github.io/P2-HR-Management-Web-Automation-Using-Playwright-Pytest-BDD/)**

---

## Highlights

- **Playwright + pytest-bdd** — a rad combo: Playwright's speed and reliability driven by Gherkin `.feature` files, so scenarios read like plain English while execution stays fast and stable.
- **Parallel execution** — tests run concurrently across CPU cores via `pytest-xdist` (`-n auto`), cutting suite runtime significantly.
- **Cross-browser out of the box** — every scenario runs against both **Chromium** and **Firefox** automatically, with no per-test setup.
- **Screenshots & videos for every test, not just failures** — one flag each in `pytest.ini` (`--screenshot=on --video=on`) captures full visual evidence for the entire run, pass or fail.
- **Everything lands in Allure** — screenshots and videos are auto-attached to their corresponding test in the Allure report, so every run is fully reviewable without digging through raw output folders.
- **Self-healing runs** — flaky steps get one automatic retry (`pytest-rerunfailures`) before being marked a real failure.
- **CI-published reports** — Jenkins runs the suite on every push and publishes the Allure report to GitHub Pages, regardless of whether tests passed or failed.

---

## Tech Stack

| Purpose | Tool |
|---|---|
| Browser automation | [Playwright](https://playwright.dev/python/) |
| BDD / Gherkin | [pytest-bdd](https://pytest-bdd.readthedocs.io/) |
| Test runner | pytest |
| Parallelization | pytest-xdist |
| Reporting | Allure Report 3 |
| Retry on flake | pytest-rerunfailures |
| CI/CD | Jenkins → GitHub Pages |

---

## Project Structure

```
.
├── features/                  # Gherkin .feature files (BDD scenarios)
├── tests/                     # Step definitions / test entry points
├── pages/                     # Page Object classes
├── page_registry.py           # Central registry wiring pages to the `pages` fixture
├── utilities/
│   └── load_json_test_data.py # Test data loader
├── test_data.json             # Shared test data
├── conftest.py                # Fixtures, Allure hooks, multi-browser wiring
├── pytest.ini                 # Pytest & plugin configuration
├── requirements.txt
└── Jenkinsfile                # CI pipeline: test → report → publish
```

---

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js (only needed locally if you want the Allure CLI to view reports)

### Install

```bash
pip install -r requirements.txt
playwright install
```

### Run the suite

```bash
pytest
```

That's it — `pytest.ini` already wires up parallel execution, both browsers, retries, screenshots, videos, and Allure result collection, so no extra flags are needed for a full run.

### View the Allure report locally

```bash
allure serve allure-results
```

---

## How It Works

### Parallel + cross-browser, configured once

`pytest.ini` drives the whole run:

```ini
addopts = --browser chromium --browser firefox -s --screenshot=on --video=on -W ignore::DeprecationWarning -n auto --alluredir=allure-results --clean-alluredir --reruns 1 --reruns-delay 3
```

- `--browser chromium --browser firefox` → every scenario is parametrized to run on both browsers automatically.
- `-n auto` (pytest-xdist) → tests distribute across all available CPU cores.
- `--screenshot=on --video=on` → Playwright captures a screenshot and video for **every** test, not only the failed ones — full visual proof of every run.
- `--reruns 1 --reruns-delay 3` → one automatic retry for transient flakiness before a test is marked failed.

A custom `_multi_browser` fixture in `conftest.py` works around a known `pytest-playwright` limitation so browser parametrization keeps working even with a custom `page` fixture wrapper.

### Screenshots & videos → added to Allure automatically

`conftest.py` hooks into `pytest_runtest_teardown` to locate each test's local Playwright output folder and attach every `.png`/`.webm` file it finds directly onto that test's entry in the Allure report — so opening a scenario in Allure shows its full recording and screenshot inline, with zero manual wiring per test.

### CI/CD pipeline

The `Jenkinsfile` runs on every push:

1. Install dependencies (Node.js for the Allure CLI, Python packages, Playwright browsers)
2. Run the full suite
3. Generate the Allure report (test failures don't block this step — the report always gets built)
4. Fetch prior Allure history for trend graphs
5. Publish the report to the `gh-pages` branch → served via GitHub Pages

---

## Object-Oriented Design

The framework is built around the **Page Object Model (POM)**, and each of the four core OOP pillars earns its place for a concrete reason rather than being bolted on for its own sake:

### Encapsulation
Every `pages/*.py` class bundles a screen's **locators and the actions that use them** into one unit, hiding Playwright selector details from anything outside the class. A step definition never touches a CSS selector directly — it calls `pages.login_page.perform_login(username, password)` and the class internally owns *how* that happens (which fields, in what order, with what waits). If OrangeHRM changes a class name or DOM structure, exactly one file needs to change.

### Inheritance
Every page object — `LoginPage`, `DashboardPage`, `AdminPage`, `ClaimPage`, `LeavePage`, `PimPage`, `SidePanelPage`, `ResetPasswordPage` — inherits from a common `BasePage`:

```python
class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded", timeout=120000)
```

`navigate_to()` (and the shared `self.page` handle) is written once and reused by every subclass, rather than each page object re-implementing its own navigation boilerplate.

### Abstraction
Test step definitions operate entirely at the level of *what* should happen (`select_employee_name(name)`, `click_assign()`, `enter_dates(from_date, to_date)`), never *how*. The "how" — dropdown-opening clicks, autocomplete waits, date-format detection and conversion, retry logic on duplicate Employee IDs — is abstracted away inside the page classes. This is what lets the `.feature` files and step definitions stay readable as plain business logic.

### Composition (favoring composition over inheritance where it fits better)
`PageRegistry` doesn't inherit from the page classes — it **composes** them, lazily instantiating each one on first access via a property:

```python
@property
def leave_page(self):
    if not self._leave_page:
        self._leave_page = LeavePage(self.page)
    return self._leave_page
```

This gives every step definition a single `pages` fixture that transparently provides any page object on demand (`pages.leave_page`, `pages.admin_page`, etc.), without paying the cost of instantiating pages that a given scenario never touches.

*Note on polymorphism*: this project doesn't lean heavily on runtime polymorphism (e.g. overriding a shared method differently per subclass) — each page's actions are specific enough to its own screen that there wasn't a natural case for it. `BasePage` is used purely as a shared-behavior base via inheritance, not as a polymorphic interface with varying implementations.

---

## Test Coverage

Scenarios are organized by feature area, each with its own `.feature` file and matching step-definition module:

| Feature File | Covers |
|---|---|
| `login.feature` | Page load/accessibility, presence and enabled-state of login fields, a Scenario Outline covering multiple valid/invalid credential combinations, and the "Forgot Password" reset flow |
| `navigation.feature` | Visibility and clickability of every main side-navigation menu item, and presence/navigation-correctness of My Info's sub-tabs |
| `user_management.feature` | End-to-end user creation via Admin → Add User (including employee lookup, role/status selection), search verification in the results table, and login validation with the freshly created credentials |
| `leave_management.feature` | Assigning leave to an employee, self-healing employee creation via PIM when the employee doesn't already exist, and cross-checking the assignment from the employee's own My Leave view |
| `claim_management.feature` | Submitting a new expense claim end-to-end and verifying it appears with the correct status in the My Claims history table |

### What's exercised beyond the happy path
- **Self-healing test data** — `leave_page.select_employee(..., create_if_missing=True)` transparently creates a missing employee via PIM mid-scenario rather than failing outright, with duplicate-Employee-ID collision handling built in for parallel runs.
- **Unique data generation per run** — usernames, employee names, and claim remarks are suffixed with a timestamp plus the running browser's initial, so chromium/firefox workers executing in parallel never collide even when they land in the same second.
- **Format-tolerant date handling** — the Assign Leave date fields are filled using whatever format OrangeHRM's own placeholder specifies (rather than a hardcoded assumption), and the My Leave table verification checks every plausible date-ordering permutation, since the app doesn't render dates consistently.
- **Case-insensitive and multi-format assertions** — profile-name and date checks tolerate the app's own inconsistencies (casing, date ordering) without weakening what's actually being verified.

---

## Using This Framework for Your Own Project

This setup is designed to be lifted into a new project with minimal changes:

1. **Copy** `pytest.ini`, `conftest.py`, `requirements.txt`, and the `Jenkinsfile`.
2. **Point it at your app** — update `base_url` in `pytest.ini`.
3. **Swap the Page Objects** — replace the contents of `pages/` and `page_registry.py` with classes for your own application's screens.
4. **Write your scenarios** — add `.feature` files under `features/` and matching step definitions under `tests/`.
5. **Wire up GitHub Pages publishing** — update `GH_PAGES_REPO` in the `Jenkinsfile`, add an SSH deploy key with write access as a Jenkins credential, and enable GitHub Pages on the `gh-pages` branch for your repo.
6. **Run it** — `pytest`. Parallelism, cross-browser coverage, retries, and full-run screenshots/videos in Allure all work immediately, with no further configuration.

The `--browser`, `-n`, `--screenshot`, `--video`, and `--reruns` flags in `pytest.ini` are the only levers most teams will ever need to touch.