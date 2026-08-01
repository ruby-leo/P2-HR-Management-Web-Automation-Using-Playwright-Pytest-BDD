import logging

from playwright.sync_api import Locator, Page
from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.username_txtbox: Locator = page.get_by_role("textbox", name="Username")
        self.password_txtbox: Locator = page.get_by_role("textbox", name="Password")
        self.login_button: Locator = page.locator("button.orangehrm-login-button")
        self.forgot_password_link: Locator = page.get_by_text("Forgot your password? ")

        # Locators for rejection / validation error messages
        self.alert_error_msg: Locator = page.locator("p.oxd-alert-content-text")
        self.input_field_error_msg: Locator = page.locator("span.oxd-input-field-error-message")

    def enter_username(self,username):
        self.username_txtbox.fill(username)
    def enter_password(self,password):
        self.password_txtbox.fill(password)
    def click_login_btn(self):
        self.login_button.click()
    def click_forgot_password(self):
        self.forgot_password_link.click()
    def perform_login(self,username,password):
        """Fills username and password, then clicks Login."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_btn()
        logging.info("entered credentials and clicked login")