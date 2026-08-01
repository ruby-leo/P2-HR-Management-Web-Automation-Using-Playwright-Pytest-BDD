# pages/leave_page.py
from datetime import datetime
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage
from pages.pim_page import PimPage
import logging
from urllib.parse import urlparse


class LeavePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation Links
        self.assign_leave_link = page.get_by_role("link", name="Assign Leave")
        self.my_leave_link = page.get_by_role("link", name="My Leave")

        # Assign Leave Form Elements
        self.employee_input = page.get_by_placeholder("Type for hints...")
        self.autocomplete_dropdown = page.locator(".oxd-autocomplete-dropdown")
        self.leave_type_dropdown = page.locator(".oxd-select-text--arrow").first
        self.dropdown_container = page.locator(".oxd-select-dropdown")

        # Date Pickers
        self.from_date_input = page.locator(".oxd-date-input input").nth(0)
        self.to_date_input = page.locator(".oxd-date-input input").nth(1)

        # Form Buttons & Feedback
        self.assign_button = page.get_by_role("button", name="Assign")
        self.confirm_ok_button = page.locator(".orangehrm-modal-footer button", has_text="Ok")
        self.success_toast = page.locator(".oxd-toast-content-text").last

        # My Leave Table Elements
        self.table_rows = page.locator(".oxd-table-card .oxd-table-row")

    def navigate_to_assign_leave(self):
        self.assign_leave_link.click()

    def select_employee(self, employee_name: str, create_if_missing: bool = False,
                        username: str = None, password: str = None) -> None:
        """Types the employee name and selects the matching option from the hint dropdown.

        If no matching employee is found and create_if_missing=True, creates the
        employee (with the given login username/password) via PIM > Add Employee
        in a separate tab, then retries the selection.
        """
        self.employee_input.fill(employee_name)
        try:
            self.autocomplete_dropdown.get_by_text(employee_name, exact=False).first.click(timeout=10000)
        except PlaywrightTimeoutError:
            if not create_if_missing:
                raise
            logging.warning(f"No records found for employee '{employee_name}' - creating via PIM > Add Employee")
            self._create_missing_employee(employee_name, username, password)
            self.employee_input.fill("")
            self.employee_input.fill(employee_name)
            self.autocomplete_dropdown.get_by_text(employee_name, exact=False).first.click(timeout=15000)

    def _create_missing_employee(self, employee_name: str, username: str, password: str):
        """Creates the given employee via PIM > Add Employee in a separate browser
        tab, then closes it - keeps this page's already-filled Assign Leave form
        state untouched while the employee is created elsewhere."""
        parsed = urlparse(self.page.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        new_tab = self.page.context.new_page()
        try:
            pim_page = PimPage(new_tab)
            pim_page.navigate_to_add_employee(base_url)
            pim_page.create_employee(employee_name, username, password)
        finally:
            new_tab.close()

    def select_leave_type(self, leave_type: str):
        """Opens the Leave Type dropdown and selects the matching item."""
        self.leave_type_dropdown.click()
        self.dropdown_container.get_by_text(leave_type, exact=True).click()

    def enter_dates(self, from_date: str, to_date: str):
        """Reads each date field's placeholder (e.g. 'yyyy-dd-mm' vs 'yyyy-mm-dd')
        to determine its expected format, converts the given dd-mm-yyyy date
        string (as written in the feature file) to match, then fills it in."""
        self._fill_date_field(self.from_date_input, from_date)
        self._fill_date_field(self.to_date_input, to_date)

    def _fill_date_field(self, field, feature_file_date_str: str):
        """Fills a single date field using its own placeholder-detected format -
        OrangeHRM's From/To date fields aren't guaranteed to share the same
        format, so each is detected and converted independently."""
        placeholder = field.get_attribute("placeholder") or "yyyy-mm-dd"
        target_format = self._strftime_format_from_placeholder(placeholder)

        parsed_date = datetime.strptime(feature_file_date_str, "%d-%m-%Y")
        formatted_value = parsed_date.strftime(target_format)
        field.clear()
        field.fill(formatted_value)

    @staticmethod
    def _strftime_format_from_placeholder(placeholder: str) -> str:
        """Converts a placeholder like 'yyyy-dd-mm' into a strftime pattern
        like '%Y-%d-%m', preserving whatever delimiter OrangeHRM is using."""
        return (
            placeholder.lower()
            .replace("yyyy", "%Y")
            .replace("mm", "%m")
            .replace("dd", "%d")
        )

    def click_assign(self):
        """Clicks Assign. OrangeHRM sometimes shows a 'Confirm Leave Assignment'
        modal (e.g. when the leave balance is insufficient) - if it appears
        within 10s, confirms it; otherwise proceeds without one."""
        self.assign_button.click()
        try:
            self.confirm_ok_button.wait_for(state="visible", timeout=10000)
            self.confirm_ok_button.click()
        except Exception:
            pass