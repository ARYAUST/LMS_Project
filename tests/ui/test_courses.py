from playwright.sync_api import expect

from pages.courses_page import CoursesPage


COURSE_TITLES = ["Python for Beginners", "Web Design Essentials", "Data Skills with SQL"]


def test_course_catalog_shows_available_courses(page, base_url):
    courses = CoursesPage(page, base_url)
    courses.open()
    for title in COURSE_TITLES:
        courses.expect_course_visible(title)


def test_student_can_search_for_a_course(page, base_url):
    courses = CoursesPage(page, base_url)
    courses.open()
    courses.search("Python")
    courses.expect_course_visible("Python for Beginners")
    expect(page.get_by_role("heading", name="Web Design Essentials")).to_have_count(0)


def test_student_can_filter_courses_by_category(page, base_url):
    courses = CoursesPage(page, base_url)
    courses.open()
    courses.filter_category("Design")
    courses.expect_course_visible("Web Design Essentials")
    expect(page.get_by_role("heading", name="Python for Beginners")).to_have_count(0)


def test_student_can_open_course_details(page, base_url):
    courses = CoursesPage(page, base_url)
    courses.open()
    courses.open_course("Python for Beginners")
    expect(page.get_by_text("Learn Python step by step with practical examples.")).to_be_visible()
    expect(page.get_by_role("link", name="Log in to enroll")).to_be_visible()


def test_empty_course_search_shows_helpful_message(page, base_url):
    courses = CoursesPage(page, base_url)
    courses.open()
    courses.search("course-that-does-not-exist")
    expect(page.get_by_text("No courses match your search.", exact=False)).to_be_visible()
