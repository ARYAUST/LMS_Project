import pytest

from utils.test_data import COURSE_DATA


@pytest.mark.api
@pytest.mark.smoke
def test_get_all_courses_returns_course_list(api_call):
    response = api_call("GET", "/api/courses")
    assert response.status == 200
    courses = response.json()
    assert len(courses) >= 3
    assert all("title" in course and "category" in course for course in courses)


@pytest.mark.api
def test_get_course_by_id_returns_course(api_call):
    response = api_call("GET", "/api/courses/1")
    assert response.status == 200
    assert response.json()["title"] == COURSE_DATA["title"]


@pytest.mark.api
def test_get_invalid_course_id_returns_not_found(api_call):
    response = api_call("GET", "/api/courses/99999")
    assert response.status == 404
    assert response.json()["error"] == "Course not found"
