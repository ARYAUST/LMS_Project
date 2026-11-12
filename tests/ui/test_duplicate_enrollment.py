from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.test_data import STUDENT

def sign_in(page, base_url):
    login = LoginPage(page, base_url)
    login.open()
    login.login(STUDENT["email"], STUDENT["password"])

def test_duplicate_enrollment_shows_clear_message(page, base_url):
    sign_in(page, base_url)
    page.goto(f"{base_url}/courses/1")
    page.get_by_role("button", name="Enroll in this course").click()
    page.goto(f"{base_url}/courses/1")
    page.get_by_role("button", name="Enroll in this course").click()
    expect(page.get_by_text("You are already enrolled in this course.", exact=True)).to_be_visible()