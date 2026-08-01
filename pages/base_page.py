from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str):
        """Navigates to the given URL. Waits only for domcontentloaded (not full
        load) with an extended 120s timeout, since the OrangeHRM demo site is
        frequently slow to finish all network activity."""
        self.page.goto(url, wait_until="domcontentloaded", timeout=120000)