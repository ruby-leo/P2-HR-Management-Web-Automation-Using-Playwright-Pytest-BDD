from playwright.sync_api import Page, Locator

from pages.base_page import BasePage


class ResetPasswordPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.reset_password_heading: Locator = page.get_by_role("heading", name="Reset Password", level=6)
        self.reset_username_txtbox: Locator = page.get_by_placeholder("Username")
        self.reset_password_button: Locator = page.locator("button.orangehrm-forgot-password-button--reset")
        self.reset_password_success_msg: Locator = page.get_by_role("heading", name="Reset Password link sent successfully", level=6)

    def enter_reset_username(self, username):
        self.reset_username_txtbox.fill(username)

    def click_reset_password_button(self):
        self.reset_password_button.click()
