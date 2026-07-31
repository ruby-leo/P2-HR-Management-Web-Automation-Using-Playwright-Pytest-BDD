# pages/pim_page.py
import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class PimPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.first_name_input = page.get_by_placeholder("First Name")
        self.last_name_input = page.get_by_placeholder("Last Name")
        self.create_login_toggle = page.locator(".oxd-switch-input").first
        self.employee_id_input = page.locator(".oxd-form .oxd-input").nth(3)
        self.username_input = page.locator(".oxd-form .oxd-input").nth(4)
        self.password_input = page.locator("input[type='password']").nth(0)
        self.confirm_password_input = page.locator("input[type='password']").nth(1)
        self.save_button = page.get_by_role("button", name="Save")
        self.success_toast = page.locator(".oxd-toast-content-text").last
        self.employee_id_error = page.locator(".oxd-input-field-error-message")

    def navigate_to_add_employee(self, base_url: str):
        self.navigate_to(f"{base_url}/web/index.php/pim/addEmployee")

    def create_employee(self, full_name: str, username: str, password: str):
        """Creates a new PIM employee AND enables login credentials for them."""
        parts = full_name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else parts[0]

        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)

        self.create_login_toggle.click()
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.confirm_password_input.fill(password)

        self.save_button.click()
        self._resolve_duplicate_employee_id_if_needed()

        expect(self.success_toast).to_contain_text("Successfully Saved", timeout=20000)
        logging.info(f"Created PIM employee '{full_name}' with login username '{username}'")

    def _resolve_duplicate_employee_id_if_needed(self, max_attempts: int = 5):
        """OrangeHRM's auto-suggested Employee Id can collide when tests run in
        parallel (-n auto). Races the error message against the success toast so
        we react to whichever appears first, instead of blindly waiting on one
        and risking the other appearing-and-dismissing in the meantime."""
        for attempt in range(1, max_attempts + 1):
            outcome = self.employee_id_error.or_(self.success_toast)
            outcome.first.wait_for(state="visible", timeout=20000)

            if self.employee_id_error.is_visible():
                current_id = self.employee_id_input.input_value().strip()
                new_id = str(int(current_id) + 5).zfill(len(current_id))
                logging.warning(
                    f"Employee Id '{current_id}' already exists "
                    f"(attempt {attempt}/{max_attempts}) - retrying with '{new_id}'"
                )
                self.employee_id_input.fill(new_id)
                self.save_button.click()
            else:
                return  # success toast won the race - save succeeded, nothing to retry

        logging.error(f"Employee Id still colliding after {max_attempts} attempts")