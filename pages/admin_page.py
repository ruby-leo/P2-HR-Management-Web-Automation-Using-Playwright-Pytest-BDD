# pages/admin_page.py
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class AdminPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation & Top Bar
        self.add_button = page.get_by_role("button", name="Add")

        # Form Elements (Add User)
        self.user_role_dropdown = page.locator(".oxd-select-text").first
        self.status_dropdown = page.locator(".oxd-select-text").nth(1)
        self.employee_name_input = page.get_by_placeholder("Type for hints...")
        self.dropdown_option_container = page.locator(".oxd-autocomplete-dropdown, .oxd-select-dropdown")

        # Username & Password Input (Index/Relative targeting for OrangeHRM form layout)
        self.username_input = page.locator(".oxd-form .oxd-input").nth(0)
        self.password_input = page.locator("input[type='password']").nth(0)
        self.confirm_password_input = page.locator("input[type='password']").nth(1)
        self.save_button = page.get_by_role("button", name="Save")

        # Search Bar Elements
        self.search_username_input = page.locator(".oxd-table-filter .oxd-input").first
        self.search_button = page.get_by_role("button", name="Search")

        # Toast & Results
        self.success_toast = page.locator(".oxd-toast-content-text").last
        self.table_rows = page.locator(".oxd-table-card .oxd-table-row")

    def click_add(self):
        self.add_button.click()

    def select_user_role(self, role: str):
        self.user_role_dropdown.click()
        self.dropdown_option_container.get_by_text(role, exact=True).click()

    def select_status(self, status: str):
        self.status_dropdown.click()
        self.dropdown_option_container.get_by_text(status, exact=True).click()

    def select_employee_name(self, name: str):
        self.employee_name_input.fill(name)
        # Wait for autocomplete hint and pick the matching employee
        self.dropdown_option_container.get_by_text(name, exact=False).first.click()

    def fill_user_credentials(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.confirm_password_input.fill(password)

    def click_save(self):
        self.save_button.click()

    def search_user(self, username: str):
        self.search_username_input.fill(username)
        self.search_button.click()