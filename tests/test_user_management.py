# tests/test_admin_user_management.py
import time
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect
from page_registry import PageRegistry

scenarios('../features/user_management.feature')

# ================================================
# Background Step
# ================================================
@given('the user is logged in as an Admin')
def logged_in_admin(pages: PageRegistry, test_data):
    """Page Registry -> login_page automatically navigates to login page"""
    pages.login_page.perform_login(
        test_data["test_admin_account_username"],
        test_data["test_admin_account_password"]
    )
    expect(pages.dashboard_page.dashboard_header).to_be_visible()

# ================================================
# Step 1: Create New User
# ================================================
@when("the user navigates to Admin > User Management > Users")
def navigate_to_user_management(pages: PageRegistry):
    pages.side_panel_page.navigate_to_the_sub_menu("Admin")

@when("clicks the Add button")
def click_add_button(pages: PageRegistry):
    pages.admin_page.click_add()

@when("fills in the new user details:")
def fill_new_user_form(pages: PageRegistry, datatable, scenario_context, browser_name):
    """Generates a unique username (timestamp + browser initial) so
    chromium/firefox workers running in parallel never collide, even if
    they hit the exact same second."""
    form_data = {row[0].strip(): row[1].strip() for row in datatable}

    unique_suffix = f"{int(time.time())}{browser_name[0]}"
    unique_username = f"{form_data['Username']}_{unique_suffix}"

    scenario_context["username"] = unique_username
    scenario_context["password"] = form_data["Password"]
    scenario_context["employee_name"] = form_data["Employee Name"]

    pages.admin_page.select_user_role(form_data["User Role"])
    pages.admin_page.select_employee_name(form_data["Employee Name"])
    pages.admin_page.select_status(form_data["Status"])
    pages.admin_page.fill_user_credentials(unique_username, form_data["Password"])

@when("clicks the Save button")
def click_save_button(pages: PageRegistry):
    pages.admin_page.click_save()

@then(parsers.parse('a success toast message "{expected_message}" should appear'))
def verify_success_toast(pages: PageRegistry, expected_message: str):
    expect(pages.admin_page.success_toast).to_be_visible()
    expect(pages.admin_page.success_toast).to_contain_text(expected_message)

# ================================================
# Step 2: Search user in Admin list
# ================================================
@when("the user searches for the newly created username in the User Management list")
def search_for_new_user(pages: PageRegistry, scenario_context):
    created_username = scenario_context["username"]
    pages.admin_page.search_user(created_username)

@then("the user should be displayed in the results table")
def verify_user_in_table(pages: PageRegistry, scenario_context):
    created_username = scenario_context["username"]
    matched_row = pages.admin_page.table_rows.filter(has_text=created_username)
    expect(matched_row).to_have_count(1)

# ================================================
# Step 3: Validate new user login
# ================================================
@when("the user logs out of the application")
def logout_user(pages: PageRegistry):
    pages.dashboard_page.logout()

@when("logs in with the newly created user credentials")
def login_with_created_credentials(pages: PageRegistry, scenario_context):
    username = scenario_context["username"]
    password = scenario_context["password"]
    pages.login_page.perform_login(username, password)

@then("the user should be logged in successfully")
def verify_login_success(pages: PageRegistry):
    expect(pages.dashboard_page.dashboard_header).to_be_visible()

@then("the top bar should display the user profile name")
def verify_profile_name(pages: PageRegistry, scenario_context):
    """Case-insensitive: OrangeHRM can render the logged-in user's name in
    a different case than it was entered in (e.g. 'nithya s' vs 'Nithya S')."""
    expected_name = scenario_context["employee_name"]
    expect(pages.dashboard_page.profile_name).to_contain_text(expected_name, ignore_case=True)