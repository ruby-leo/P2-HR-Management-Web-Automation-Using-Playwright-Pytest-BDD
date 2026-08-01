from playwright.sync_api import Page, Locator

from pages.base_page import BasePage


class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.dashboard_header: Locator = page.get_by_role("heading", name="Dashboard", level=6)
        self.user_dropdown = page.locator(".oxd-userdropdown-tab")
        self.profile_name = page.locator(".oxd-userdropdown-name")
        self.logout_link = page.get_by_role("menuitem", name="Logout")

    def logout(self):
        """Opens the user profile dropdown and clicks Logout."""
        self.user_dropdown.click()
        self.logout_link.click()