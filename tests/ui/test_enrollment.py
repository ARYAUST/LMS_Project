from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.test_data import STUDENT


def sign_in(page, base_url):
    login = LoginPage(page, base_url)
    login.open()
    login.login(STUDENT["email"], STUDENT["password"])


def test_student_can_enroll_in_course(page, base_url):
    sign_in(page, base_url)
    page.goto(f"{base_url}/courses")
    page.get_by_role("link", name="Python for Beginners").click()
    page.get_by_role("button", name="Enroll in this course").click()
    expect(page.get_by_text("You are enrolled!", exact=True)).to_be_visible()
    DashboardPage(page, base_url).expect_course("Python for Beginners")


def test_duplicate_enrollment_shows_clear_message(page, base_url):
    sign_in(page, base_url)
    page.goto(f"{base_url}/courses/1")
    page.get_by_role("button", name="Enroll in this course").click()
    page.goto(f"{base_url}/courses/1")
    page.get_by_role("button", name="Enroll in this course").click()
    expect(page.get_by_text("You are already enrolled in this course.", exact=True)).to_be_visible()


def test_enrolled_course_appears_on_student_dashboard(page, base_url):
    sign_in(page, base_url)
    page.goto(f"{base_url}/courses/1")
    page.get_by_role("button", name="Enroll in this course").click()
    dashboard = DashboardPage(page, base_url)
    dashboard.open()
    dashboard.expect_course("Python for Beginners")
    expect(page.get_by_text("Progress")).to_be_visible()


def test_dashboard_navigation_is_available_after_login(page, base_url):
    sign_in(page, base_url)
    page.get_by_role("link", name="Courses").click()
    expect(page.get_by_role("heading", name="Find your next skill.")).to_be_visible()
    page.get_by_role("link", name="My learning").click()
    expect(page.get_by_role("heading", name="Welcome, Taylor Student.")).to_be_visible()
