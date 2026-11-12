"""Page object for the student dashboard."""

from playwright.sync_api import Page, expect


class DashboardPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/dashboard")

    def expect_welcome(self, name: str) -> None:
        expect(self.page.get_by_role("heading", name=f"Welcome, {name}.")).to_be_visible()

    def expect_course(self, title: str) -> None:
        expect(self.page.get_by_role("heading", name=title)).to_be_visible()
