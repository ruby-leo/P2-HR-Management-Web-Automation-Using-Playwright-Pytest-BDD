from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.reset_password_page import ResetPasswordPage
from pages.side_panel_page import SidePanelPage
from pages.claim_page import ClaimPage
from pages.leave_page import LeavePage
from pages.admin_page import AdminPage
from pages.pim_page import PimPage


class PageRegistry:
    """Lazily builds and caches one Page Object per OrangeHRM screen.

    Step definitions pull whichever page they need off this registry
    (e.g. `pages.leave_page`) instead of importing and constructing Page
    Objects directly. Each page is only instantiated on first access.
    """

    def __init__(self, page, request):
        self.page = page
        self.request = request
        self._login_page = None
        self._dashboard_page = None
        self._reset_password_page = None
        self._side_panel_page = None
        self._claim_page = None
        self._leave_page = None
        self._admin_page = None
        self._pim_page = None

    @property
    def login_page(self):
        """Login page - navigates to base_url on first access."""
        if not self._login_page:
            self._login_page = LoginPage(self.page)
            base_url = self.request.config.getoption("--base-url") or self.request.config.getini("base_url")
            self._login_page.navigate_to(base_url)
        return self._login_page

    @property
    def reset_password_page(self):
        """Forgot-password / reset-password page."""
        if not self._reset_password_page:
            self._reset_password_page = ResetPasswordPage(self.page)
        return self._reset_password_page

    @property
    def dashboard_page(self):
        """Post-login landing dashboard."""
        if not self._dashboard_page:
            self._dashboard_page = DashboardPage(self.page)
        return self._dashboard_page

    @property
    def side_panel_page(self):
        """Left-hand navigation menu, present on every authenticated page."""
        if not self._side_panel_page:
            self._side_panel_page = SidePanelPage(self.page)
        return self._side_panel_page

    @property
    def claim_page(self):
        """Claim module."""
        if not self._claim_page:
            self._claim_page = ClaimPage(self.page)
        return self._claim_page

    @property
    def leave_page(self):
        """Leave module."""
        if not self._leave_page:
            self._leave_page = LeavePage(self.page)
        return self._leave_page

    @property
    def admin_page(self):
        """Admin module (user management, system config)."""
        if not self._admin_page:
            self._admin_page = AdminPage(self.page)
        return self._admin_page

    @property
    def pim_page(self):
        """PIM module (employee records)."""
        if not self._pim_page:
            self._pim_page = PimPage(self.page)
        return self._pim_page