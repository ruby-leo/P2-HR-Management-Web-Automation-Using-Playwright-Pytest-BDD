from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect

from page_registry import PageRegistry

# Load all scenarios from the navigation feature file
scenarios('../features/navigation.feature')

# ================================
# Shared / Common Background Steps
# ================================
@given("the user is logged into OrangeHRM with valid credentials")
def logged_in_user(pages: PageRegistry):
    """Page Registry -> login_page automatically navigates to login page"""
    pages.login_page.perform_login('Admin', 'admin123')
    expect(pages.dashboard_page.dashboard_header).to_be_visible()

# =================================================================================
# Scenario @TC-04: Verify visibility and clickability of main navigation menu items
# =================================================================================
@then("the side navigation panel should display the following items:", target_fixture="expected_menu_items")
def verify_side_menu_items(pages: PageRegistry, datatable):
    """Has a Gherkin table, so datatable is used. Returns the expected item
    names as target_fixture so the next step (which has no table of its own)
    can reuse the same list instead of duplicating it."""
    expected_menu_items = [row[0] for row in datatable]
    for item_name in expected_menu_items:
        side_menu_item = pages.side_panel_page.get_side_menu_item(item_name)
        expect(side_menu_item).to_be_visible()
    return expected_menu_items

@then("each menu item should be visible and clickable")
def verify_side_menu_clickable(pages: PageRegistry, expected_menu_items):
    for item_name in expected_menu_items:
        side_menu_item = pages.side_panel_page.get_side_menu_item(item_name)
        expect(side_menu_item).to_be_visible()
        expect(side_menu_item).to_be_enabled()

# ==============================================================================================
# Scenario @TC-08: Validate presence and accessibility of sub-menu items under My Info
# ==============================================================================================
@when('the user navigates to the My Info section')
def navigate_to_my_info_section(pages: PageRegistry):
    pages.side_panel_page.navigate_to_the_sub_menu("My Info")

@then("the following sub-tabs should be visible and accessible:", target_fixture="expected_sub_tabs")
def verify_sub_tabs_visible(pages: PageRegistry, datatable):
    expected_sub_tabs = [row[0] for row in datatable]
    for sub_tab_name in expected_sub_tabs:
        sub_tab_locator = pages.side_panel_page.get_sub_tab_locator(sub_tab_name)
        expect(sub_tab_locator).to_be_visible()
        expect(sub_tab_locator).to_be_enabled()
    return expected_sub_tabs

@then("clicking each sub-tab should navigate to its corresponding details page")
def click_and_verify_each_sub_tab(pages: PageRegistry, expected_sub_tabs):
    for tab_name in expected_sub_tabs:
        sub_tab_locator = pages.side_panel_page.get_sub_tab_locator(tab_name)
        pages.side_panel_page.click_sub_tab_locator(sub_tab_locator)
        expect(pages.side_panel_page.sub_tab_title).to_contain_text(tab_name)