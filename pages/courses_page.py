"""Page object for course browsing, filtering, details, and enrollment."""

from playwright.sync_api import Page, expect


class CoursesPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/courses")

    def search(self, phrase: str) -> None:
        self.page.get_by_label("Search courses").fill(phrase)
        self.page.get_by_role("button", name="Search").click()

    def filter_category(self, category: str) -> None:
        self.page.get_by_label("Category").select_option(label=category)
        self.page.get_by_role("button", name="Search").click()

    def open_course(self, title: str) -> None:
        self.page.get_by_role("link", name=title).click()

    def expect_course_visible(self, title: str) -> None:
        expect(self.page.get_by_role("heading", name=title)).to_be_visible()
