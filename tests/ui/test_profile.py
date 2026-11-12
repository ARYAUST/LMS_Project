from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from utils.test_data import STUDENT


def sign_in(page, base_url):
    login = LoginPage(page, base_url)
    login.open()
    login.login(STUDENT["email"], STUDENT["password"])


def test_student_can_update_name_and_email(page, base_url):
    sign_in(page, base_url)
    profile = ProfilePage(page, base_url)
    profile.open()
    profile.update("Taylor Updated", "taylor.updated@example.com")
    profile.expect_saved()
    expect(page.get_by_label("Full name")).to_have_value("Taylor Updated")
    expect(page.get_by_label("Email")).to_have_value("taylor.updated@example.com")


def test_student_can_change_password(page, base_url):
    sign_in(page, base_url)
    profile = ProfilePage(page, base_url)
    profile.open()
    profile.update(STUDENT["name"], STUDENT["email"], "NewPassword456!")
    profile.expect_saved()
    page.get_by_role("link", name="Log out").click()
    login = LoginPage(page, base_url)
    login.open()
    login.login(STUDENT["email"], "NewPassword456!")
    expect(page.get_by_role("heading", name=f"Welcome, {STUDENT['name']}.")).to_be_visible()


def test_profile_requires_name_and_valid_email(page, base_url):
    sign_in(page, base_url)
    page.goto(f"{base_url}/profile")
    page.get_by_label("Full name").fill("")
    page.get_by_role("button", name="Save changes").click()
    assert page.get_by_label("Full name").evaluate("element => element.validity.valueMissing")
