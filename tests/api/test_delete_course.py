import pytest


@pytest.mark.api
def test_delete_course_returns_no_content_and_removes_course(api_call):
    response = api_call("DELETE", "/api/courses/1")
    assert response.status == 204
    missing = api_call("GET", "/api/courses/1")
    assert missing.status == 404
