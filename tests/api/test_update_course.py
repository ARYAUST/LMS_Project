import pytest

from utils.test_data import COURSE_DATA


@pytest.mark.api
def test_put_replaces_course_fields(api_call):
    updated = {**COURSE_DATA, "title": "Python Foundations", "category": "Software"}
    response = api_call("PUT", "/api/courses/1", data=updated)
    assert response.status == 200
    assert response.json()["title"] == "Python Foundations"
    assert response.json()["category"] == "Software"


@pytest.mark.api
def test_patch_updates_only_requested_field(api_call):
    response = api_call("PATCH", "/api/courses/1", data={"title": "Python Essentials"})
    assert response.status == 200
    assert response.json()["title"] == "Python Essentials"
    assert response.json()["category"] == "Programming"
