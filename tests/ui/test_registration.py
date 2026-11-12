import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage


@pytest.mark.regression
def test_new_student_can_register(page, base_url):
    LoginPage(page, base_url).register("Jamie Learner", "jamie@example.com", "SecurePass123!")
    expect(page.get_by_text("Account created. Please log in.", exact=True)).to_be_visible()
    expect(page).to_have_url(f"{base_url}/login")


def test_registration_rejects_duplicate_email(page, base_url):
    LoginPage(page, base_url).register("Another Student", "student@example.com", "SecurePass123!")
    expect(page.get_by_text("An account with that email already exists.", exact=True)).to_be_visible()


def test_registration_requires_all_fields(page, base_url):
    page.goto(f"{base_url}/register")
    page.get_by_role("button", name="Create account").click()
    assert page.get_by_label("Full name").evaluate("element => element.validity.valueMissing")
    assert page.get_by_label("Email").evaluate("element => element.validity.valueMissing")
    assert page.get_by_label("Password").evaluate("element => element.validity.valueMissing")


def test_registration_rejects_malformed_email(page, base_url):
    page.goto(f"{base_url}/register")
    page.get_by_label("Full name").fill("Jamie Learner")
    page.get_by_label("Email").fill("not-an-email")
    page.get_by_label("Password").fill("SecurePass123!")
    page.get_by_role("button", name="Create account").click()
    assert page.get_by_label("Email").evaluate("element => element.validity.typeMismatch")
