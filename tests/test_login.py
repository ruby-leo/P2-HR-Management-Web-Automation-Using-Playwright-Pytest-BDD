import logging
import re
from pytest_bdd import scenarios, given, when, then, parsers, step
from playwright.sync_api import expect

from playwright.sync_api import Page
from page_registry import PageRegistry

# Load all scenarios from the login feature file
scenarios('../features/login.feature')


# ==============================================================================
# Shared / Common Background Steps
# ==============================================================================

@given("the user launches the browser")
def launch_browser():
    """Managed automatically by Playwright's page fixture."""
    pass

@when('the user navigates to login page')
@step("the user navigates to the OrangeHRM login page")
@given("the user is on the OrangeHRM login page")
def navigate_to_login_page(pages: PageRegistry):
    """Managed automatically by Page Registry -> login_page"""
    pass

# ==============================================================================
# Scenario @TC-02: Verify OrangeHRM URL accessibility
# ==============================================================================
@then("the login page should load successfully without errors")
def verify_login_page_loaded(pages: PageRegistry, page: Page):
    expect(pages.login_page.username_txtbox).to_be_visible()

# ==============================================================================
# Scenario @TC-03: Validate presence and state of login input fields
# ==============================================================================
@then('the "Username" input field should be visible and enabled')
def verify_username_field(pages: PageRegistry):
    expect(pages.login_page.username_txtbox).to_be_visible()
    expect(pages.login_page.username_txtbox).to_be_enabled()

@then('the "Password" input field should be visible and enabled')
def verify_password_field(pages: PageRegistry):
    expect(pages.login_page.password_txtbox).to_be_visible()
    expect(pages.login_page.password_txtbox).to_be_enabled()

@then('the "Login" button should be visible and clickable')
def verify_login_button(pages: PageRegistry):
    expect(pages.login_page.login_button).to_be_visible()
    expect(pages.login_page.login_button).to_be_enabled()

# =======================================================================================
# Scenario Outline @TC-01: Validate login functionality with multiple sets of credentials
# =======================================================================================
@when(parsers.re(r'the user enters username "(?P<username>[^"]*)" and password "(?P<password>[^"]*)"'))
def enter_credentials(pages: PageRegistry, username: str, password: str):
    pages.login_page.enter_username(username)
    pages.login_page.enter_password(password)

@when('clicks the Login button')
def click_login(pages: PageRegistry):
    pages.login_page.click_login_btn()

@then(parsers.parse('the login outcome should be "{expected_result}"'))
def verify_login_outcome(pages: PageRegistry, expected_result: str):
    """For a 'Success' outcome, checks the dashboard loaded; for any failure
    outcome, checks the login button is still present (user stayed on the
    login page rather than being redirected)."""
    if expected_result == "Success":
        expect(pages.dashboard_page.dashboard_header).to_be_visible()
    else:
        expect(pages.login_page.login_button).to_be_visible()

@then(parsers.parse('an appropriate message "{message}" should be displayed if rejected'))
def verify_rejection_message(pages: PageRegistry, message: str):
    """Skips the check when message == 'Dashboard' - that value signals a
    successful login (no rejection message expected) for this Scenario
    Outline's shared step."""
    if message != "Dashboard":
        error_locator = pages.login_page.alert_error_msg.or_(pages.login_page.input_field_error_msg)
        expect(error_locator).to_contain_text(message)

# ==============================================================================
# Scenario @TC-07: Verify "Forgot Password" functionality
# ==============================================================================
@when('the user clicks on the "Forgot your password?" link')
def click_forgot_password(pages: PageRegistry):
    pages.login_page.click_forgot_password()

@then('the user should be redirected to the Reset Password page')
def verify_redirection(pages: PageRegistry):
        expect(pages.reset_password_page.reset_password_heading).to_be_visible()

@when(parsers.re(r'^the user enters username "(?P<username>[^"]*)"$'))
def enter_reset_username(pages: PageRegistry, username: str):
    pages.reset_password_page.enter_reset_username(username)

@when('clicks the "Reset Password" button')
def click_reset_password(pages: PageRegistry):
    pages.reset_password_page.click_reset_password_button()

@then('a confirmation message Reset Password link sent successfully should appear')
def verify_reset_confirmation(pages: PageRegistry):
    expect(pages.reset_password_page.reset_password_success_msg).to_be_visible()