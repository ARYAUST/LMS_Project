"""Page object for student profile editing."""

from playwright.sync_api import Page, expect


class ProfilePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/profile")

    def update(self, name: str, email: str, password: str = "") -> None:
        self.page.get_by_label("Full name").fill(name)
        self.page.get_by_label("Email").fill(email)
        self.page.get_by_label("New password").fill(password)
        self.page.get_by_role("button", name="Save changes").click()

    def expect_saved(self) -> None:
        expect(self.page.get_by_text("Profile updated.", exact=True)).to_be_visible()
