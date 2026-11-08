import pytest
import requests

import sjsu_rmp_collect as module
from models import Semester


class FakeResponse:
    def __init__(self, text="", error=None):
        self.text = text
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error


@pytest.fixture
def collector():
    return module.Collector()


def test_get_semester_url_returns_url(monkeypatch, collector):
    html = """
    <li>
        <a href="/classes/fall2026">
            Fall 2026 Class Schedule
        </a>
    </li>
    """

    def fake_get(url):
        assert url == (
            "https://www.sjsu.edu"
            "/classes/schedules/index.php"
        )
        return FakeResponse(html)

    monkeypatch.setattr(module.requests, "get", fake_get)

    result = collector._get_semester_url(Semester.FALL, 2026)

    assert result == "/classes/fall2026"


def test_get_semester_url_raises_http_error(monkeypatch, collector):
    response = FakeResponse(
        error=requests.HTTPError("Request failed")
    )

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: response,
    )

    with pytest.raises(requests.HTTPError, match="Request failed"):
        collector._get_semester_url(Semester.FALL, 2026)


def test_get_semester_url_raises_when_not_found(monkeypatch, collector):
    html = """
    <li>
        <a href="/classes/spring2026">
            Spring 2026 Class Schedule
        </a>
    </li>
    """

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FakeResponse(html),
    )

    with pytest.raises(module.SemesterNotFoundError) as exception_info:
        collector._get_semester_url(Semester.FALL, 2026)

    error = exception_info.value

    assert error.semester == Semester.FALL
    assert error.year == 2026
    assert str(error) == "Semester not found: Fall 2026"


def test_get_semester_url_raises_when_not_published(
    monkeypatch,
    collector,
):
    html = "<a>Fall 2026 Class Schedule</a>"

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FakeResponse(html),
    )

    with pytest.raises(module.SemesterNotFoundError) as exception_info:
        collector._get_semester_url(Semester.FALL, 2026)

    error = exception_info.value

    assert error.semester == Semester.FALL
    assert error.year == 2026
    assert str(error) == (
        "Semester has not been published: Fall 2026"
    )