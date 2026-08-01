from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

from page_registry import PageRegistry
from datetime import datetime

# Load all scenarios from the claim management feature file
scenarios('../features/claim_management.feature')

# ================================================
# Shared Background Steps
# ================================================
@given("the user is logged in as an employee")
def logged_in_employee(pages: PageRegistry):
    """Page Registry -> login_page automatically navigates to login page"""
    pages.login_page.perform_login('Admin', 'admin123')
    expect(pages.dashboard_page.dashboard_header).to_be_visible()

# =================================================================================
# Scenario @TC-10: Initiate and submit a new expense claim request
# =================================================================================
@when("the user navigates to the Claim section")
def navigate_to_claim_section(pages: PageRegistry):
    pages.side_panel_page.navigate_to_the_sub_menu("Claim")

@when("clicks on Submit Claim")
def click_submit_claim_tab(pages: PageRegistry):
    pages.claim_page.submit_claim_link.click()

@when("selects Event Accommodation and Currency and enter reason")
def fill_claim_details(pages: PageRegistry, scenario_context, browser_name):
    """Generates remarks unique per run (timestamp + browser initial) so
    chromium/firefox workers running in parallel never produce identical
    remarks even if they land in the same second - stored in scenario_context
    so later steps can filter the claims table for this exact submission."""
    pages.claim_page.select_event_option("Travel Allowance")
    pages.claim_page.select_currency_option("Indian Rupee")

    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unique_remarks = f"Business Travel on {current_time_str}{browser_name[0]}"
    scenario_context["unique_remarks"] = unique_remarks

    pages.claim_page.enter_remarks(unique_remarks)

@when('clicks "Create"')
def click_create_button(pages: PageRegistry):
    pages.claim_page.click_create()

@then("a success confirmation message should be displayed")
def verify_success_toast(pages: PageRegistry):
    expect(pages.claim_page.success_toast_content).to_be_visible()
    expect(pages.claim_page.success_toast_content).to_contain_text("Successfully Saved")

@when('the user checks the "My Claims" history table')
def open_my_claims_tab(pages: PageRegistry, page):
    """Waits before navigating - immediate navigation to My Claims can land
    on a stale/mixed-up page state right after a claim submission."""
    page.wait_for_timeout(5000)
    pages.claim_page.my_claims_link.click()

@then("the newly submitted claim should be listed with status Initiated")
def verify_submitted_claim_in_table(pages: PageRegistry, scenario_context):
    claim_row = (
        pages.claim_page.table_rows
        .filter(has_text="Travel Allowance")
        .filter(has_text="Indian Rupee")
        .filter(has_text=scenario_context["unique_remarks"])
    )
    expect(claim_row).to_have_count(1)