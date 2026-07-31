from playwright.sync_api import Page

from pages.base_page import BasePage


class ClaimPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.submit_claim_link = page.get_by_role('link', name="Submit Claim")
        self.event_dropdown = page.locator(".oxd-select-text--arrow").first
        self.currency_dropdown = page.locator(".oxd-select-text--arrow").last
        self.dropdown_container = page.locator(".oxd-select-dropdown")
        self.remarks_textarea = page.locator(".oxd-textarea")
        self.create_button = page.get_by_role("button", name="Create")
        self.success_toast_content = page.locator(".oxd-toast-content-text").last
        self.my_claims_link = page.get_by_role('link', name="My Claims")
        self.table_rows = page.locator(".oxd-table-card .oxd-table-row")

    def select_event_option(self, option_name: str):
        """Opens the event dropdown and selects the specified option by text."""
        self.event_dropdown.click()
        self.dropdown_container.get_by_text(option_name, exact=True).click()

    def select_currency_option(self, option_name: str):
        """Opens the currency dropdown and selects the specified option by text."""
        self.currency_dropdown.click()
        self.dropdown_container.get_by_text(option_name, exact=True).click()

    def enter_remarks(self, text: str):
        """Fills out the Remarks textarea field."""
        self.remarks_textarea.fill(text)

    def click_create(self):
        self.create_button.click()

    def verify_claim_in_row(self, event: str, remarks: str, currency: str):
        """Filters the rows to find one containing all three targeted values."""
        target_row = (
            self.table_rows
            .filter(has_text=event)
            .filter(has_text=remarks)
            .filter(has_text=currency)
        )

