"""Shared, readable test data used by UI and API tests."""

BASE_URL = "http://127.0.0.1:5000"

STUDENT = {
    "name": "Taylor Student",
    "email": "student@example.com",
    "password": "StudentPass123!",
}

INVALID_LOGIN_CASES = [
    ("missing.user@example.com", "WrongPass123!", "Invalid email or password"),
    (STUDENT["email"], "wrong-password", "Invalid email or password"),
]

COURSE_DATA = {
    "title": "Python for Beginners",
    "description": "Learn Python step by step with practical examples.",
    "category": "Programming",
    "instructor": "Morgan Lee",
}
