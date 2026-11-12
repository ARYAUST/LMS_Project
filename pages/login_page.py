"""Page object for login and registration forms."""

from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/login")

    def login(self, email: str, password: str) -> None:
        self.page.get_by_label("Email").fill(email)
        self.page.get_by_label("Password").fill(password)
        self.page.get_by_role("button", name="Log in").click()

    def expect_error(self, message: str) -> None:
        expect(self.page.get_by_text(message, exact=True)).to_be_visible()

    def register(self, name: str, email: str, password: str) -> None:
        self.page.goto(f"{self.base_url}/register")
        self.page.get_by_label("Full name").fill(name)
        self.page.get_by_label("Email").fill(email)
        self.page.get_by_label("Password").fill(password)
        self.page.get_by_role("button", name="Create account").click()
