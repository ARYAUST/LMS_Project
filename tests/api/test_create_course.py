import pytest

from utils.test_data import COURSE_DATA


@pytest.mark.api
def test_create_course_returns_created_course(api_call):
    response = api_call("POST", "/api/courses", data=COURSE_DATA)
    assert response.status == 201
    assert response.json()["title"] == COURSE_DATA["title"]
    assert response.json()["id"] > 0


@pytest.mark.api
@pytest.mark.parametrize("payload", [{}, {"title": "Incomplete"}, None])
def test_create_course_rejects_invalid_data(api_call, payload):
    response = api_call("POST", "/api/courses", data=payload)
    assert 400 <= response.status < 500
    assert "error" in response.json()
