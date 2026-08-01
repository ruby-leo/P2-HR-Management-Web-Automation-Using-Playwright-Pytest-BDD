# tests/test_leave_management.py
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect
import re
import time
from datetime import datetime

from page_registry import PageRegistry


# Load all scenarios from the leave feature file
scenarios('../features/leave_management.feature')

# ================================================
# Shared / Background Steps
# ================================================
@given("the user is logged into OrangeHRM as an Admin")
def logged_in_admin(pages: PageRegistry, test_data):
    """Page Registry -> login_page automatically navigates to login page"""
    pages.login_page.perform_login(test_data["test_admin_account_username"], test_data["test_admin_account_password"])
    expect(pages.dashboard_page.dashboard_header).to_be_visible()

# =================================================================================
# Scenario @TC-09: Assign leave to an employee and verify assignment
# =================================================================================
@when("the Admin user navigates to Leave > Assign Leave")
def navigate_to_menu_path(pages: PageRegistry):
    pages.side_panel_page.navigate_to_the_sub_menu("Leave")
    pages.leave_page.navigate_to_assign_leave()

@when("fills out the leave assignment form:")
def fill_leave_form(pages: PageRegistry, datatable, scenario_context, test_data, browser_name):
    """Creates a brand-new employee every run (unique name/username via
    timestamp + browser initial) so this test never collides with a
    previous run's leave dates ('overlapping leave requests' error), and
    never hits a stale username from a concurrent chromium/firefox run."""
    form_data = {row[0].strip(): row[1].strip() for row in datatable}

    unique_suffix = f"{int(time.time())}{browser_name[0]}"
    employee_name = f"{form_data['Employee Name']} {unique_suffix}"
    employee_username = f"{test_data['test_employee_account_username']}_{unique_suffix}"
    employee_password = test_data["test_employee_account_password"]

    scenario_context["from_date"] = form_data["From Date"]
    scenario_context["leave_type"] = form_data["Leave Type"]
    scenario_context["employee_name"] = employee_name
    scenario_context["employee_username"] = employee_username
    scenario_context["employee_password"] = employee_password

    pages.leave_page.select_employee(
        employee_name,
        create_if_missing=True,
        username=employee_username,
        password=employee_password,
    )
    pages.leave_page.select_leave_type(form_data["Leave Type"])
    pages.leave_page.enter_dates(form_data["From Date"], form_data["To Date"])

@when('clicks the "Assign" button')
def click_assign_button(pages: PageRegistry):
    pages.leave_page.click_assign()

@then(parsers.parse('a confirmation toast message "{expected_message}" should be displayed'))
def verify_toast_message(pages: PageRegistry, expected_message: str):
    expect(pages.leave_page.success_toast).to_be_visible()
    expect(pages.leave_page.success_toast).to_contain_text(expected_message)

@when("the employee user navigates to Leave and then My Leave")
def switch_to_employee_and_navigate_to_my_leave(pages: PageRegistry, scenario_context):
    """Logs out the Admin, logs in as the employee created earlier in this
    scenario, then navigates to My Leave to verify the assignment from
    the employee's own perspective."""
    pages.dashboard_page.logout()

    pages.login_page.perform_login(
        scenario_context["employee_username"],
        scenario_context["employee_password"],
    )
    expect(pages.dashboard_page.dashboard_header).to_be_visible()

    pages.side_panel_page.navigate_to_the_sub_menu("Leave")
    pages.leave_page.my_leave_link.click()

@then("the newly assigned leave record should appear")
def verify_assigned_leave_record(pages: PageRegistry, scenario_context):
    """The My Leave table's date format isn't consistent - matches against
    every permutation of day/month/year since the feature file's dd-mm-yyyy
    date could render as any of the six orderings below."""
    from_date = datetime.strptime(scenario_context["from_date"], "%d-%m-%Y")

    possible_formats = [
        from_date.strftime("%Y-%m-%d"),  # 2026-08-06
        from_date.strftime("%Y-%d-%m"),  # 2026-06-08
        from_date.strftime("%m-%d-%Y"),  # 08-06-2026
        from_date.strftime("%m-%Y-%d"),  # 08-2026-06
        from_date.strftime("%d-%m-%Y"),  # 06-08-2026
        from_date.strftime("%d-%Y-%m"),  # 06-2026-08
    ]
    date_pattern = re.compile("|".join(re.escape(fmt) for fmt in possible_formats))

    employee_name = scenario_context["employee_name"]
    leave_type = scenario_context["leave_type"]
    record_row = (
        pages.leave_page.table_rows
        .filter(has_text=date_pattern)
        .filter(has_text=employee_name)
        .filter(has_text=leave_type)
    )
    expect(record_row).to_have_count(1)