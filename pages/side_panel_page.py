from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class SidePanelPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.side_menu_item = lambda item_name: (page.locator("span.oxd-main-menu-item--name",has_text=item_name))
        self.sub_tabs = lambda item_name: (page.locator("a.orangehrm-tabs-item", has_text=item_name))
        self.sub_tab_title = page.locator("h6.orangehrm-main-title").first

    def get_side_menu_item(self, item_name: str):
        """Returns the locator for a specific main menu item by name."""
        return self.side_menu_item(item_name)
    def get_sub_tab_locator(self, sub_tab_name: str):
        return self.sub_tabs(sub_tab_name)
    def click_sub_tab_locator(self, sub_tab_locator):
        sub_tab_locator.click()
    def navigate_to_the_sub_menu(self, sub_menu_name):
        self.side_menu_item(sub_menu_name).click()