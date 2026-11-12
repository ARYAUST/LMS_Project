import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from utils.test_data import INVALID_LOGIN_CASES, STUDENT


@pytest.mark.smoke
@pytest.mark.parametrize("email,password,error", INVALID_LOGIN_CASES)
def test_invalid_login_shows_error(page, base_url, email, password, error):
    login = LoginPage(page, base_url)
    login.open()
    login.login(email, password)
    login.expect_error(error)


@pytest.mark.smoke
def test_student_can_log_in(page, base_url):
    login = LoginPage(page, base_url)
    login.open()
    login.login(STUDENT["email"], STUDENT["password"])
    expect(page.get_by_role("heading", name=f"Welcome, {STUDENT['name']}.")).to_be_visible()


def test_empty_login_fields_are_required(page, base_url):
    LoginPage(page, base_url).open()
    page.get_by_role("button", name="Log in").click()
    assert page.get_by_label("Email").evaluate("element => element.validity.valueMissing")
    assert page.get_by_label("Password").evaluate("element => element.validity.valueMissing")


def test_logout_returns_to_course_catalog(page, base_url):
    login = LoginPage(page, base_url)
    login.open()
    login.login(STUDENT["email"], STUDENT["password"])
    page.get_by_role("link", name="Log out").click()
    expect(page.get_by_role("heading", name="Find your next skill.")).to_be_visible()
    expect(page.get_by_role("link", name="Log in")).to_be_visible()


def test_dashboard_shows_student_content_after_login(page, base_url):
    login = LoginPage(page, base_url)
    login.open()
    login.login(STUDENT["email"], STUDENT["password"])
    expect(page.get_by_text("Your learning, all in one place.")).to_be_visible()
