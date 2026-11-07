import requests
import pytest

import sjsu_rmp_collect as module
from models import Course, Professor, Rating, Request, Semester


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


def test_parse_professor_stats_returns_rating(
    monkeypatch,
    collector,
):
    html = """
    <html>
        <body>
            <div class="RatingValue__Numerator-qw8sqy-2 duhvlP">
                4.5
            </div>

            <div class="FeedbackItem__FeedbackNumber-uof32n-1 ecFgca">
                2.8
            </div>

            <span class="Tag-bs9vf4-0 bmtbjB">
                Tough grader
            </span>

            <span class="Tag-bs9vf4-0 bmtbjB">
                EXTRA CREDIT
            </span>
        </body>
    </html>
    """

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FakeResponse(html),
    )

    result = collector._parse_professor_stats(
        "https://example.com/professor/123"
    )

    assert result == Rating(
        quality=4.5,
        difficulty=2.8,
        tags={"TOUGH GRADER", "EXTRA CREDIT"},
    )


def test_parse_professor_stats_handles_missing_difficulty(
    monkeypatch,
    collector,
):
    html = """
    <html>
        <body>
            <div class="RatingValue__Numerator-qw8sqy-2 duhvlP">
                4.0
            </div>
        </body>
    </html>
    """

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FakeResponse(html),
    )

    result = collector._parse_professor_stats(
        "https://example.com/professor/123"
    )

    assert result.quality == 4.0
    assert result.difficulty == "N/A"
    assert result.tags == set()


def test_parse_professor_stats_handles_na_quality(
    monkeypatch,
    collector,
):
    html = """
    <html>
        <body>
            <div class="RatingValue__Numerator-qw8sqy-2 duhvlP">
                N/A
            </div>

            <div class="FeedbackItem__FeedbackNumber-uof32n-1 ecFgca">
                N/A
            </div>
        </body>
    </html>
    """

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FakeResponse(html),
    )

    result = collector._parse_professor_stats(
        "https://example.com/professor/123"
    )

    assert result.quality == "N/A"
    assert result.difficulty == "N/A"
    assert result.tags == set()


def test_parse_professor_stats_propagates_http_error(
    monkeypatch,
    collector,
):
    response = FakeResponse(
        error=requests.HTTPError("Request failed")
    )

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: response,
    )

    with pytest.raises(requests.HTTPError, match="Request failed"):
        collector._parse_professor_stats(
            "https://example.com/professor/123"
        )


def test_get_professor_statistics_updates_professor_rating(
    monkeypatch,
    collector,
):
    professor = Professor(
        name="John Smith",
        email="john@example.com",
    )

    collector._Collector__professors["John Smith"] = professor

    search_html = """
    <a
        class="TeacherCard__StyledTeacherCard-syjs0d-0 eerjaA"
        href="/professor/12345"
    >
        John Smith
    </a>
    """

    rating = Rating(
        quality=4.5,
        difficulty=2.5,
        tags={"HELPFUL"},
    )

    requested_urls = []
    parsed_urls = []

    def fake_get(url):
        requested_urls.append(url)
        return FakeResponse(search_html)

    def fake_parse(url):
        parsed_urls.append(url)
        return rating

    monkeypatch.setattr(module.requests, "get", fake_get)
    monkeypatch.setattr(
        collector,
        "_parse_professor_stats",
        fake_parse,
    )

    collector._get_professor_statistics("John Smith")

    expected_search_url = (
        f"{collector._Collector__SJSU_RMP_URL}"
        "John%20Smith"
    )

    assert requested_urls == [expected_search_url]
    assert parsed_urls == [
        "https://www.ratemyprofessors.com/professor/12345"
    ]
    assert professor.rating == rating


def test_get_professor_statistics_does_nothing_for_unknown_professor(
    monkeypatch,
    collector,
):
    def fail_if_called(url):
        pytest.fail("requests.get should not be called")

    monkeypatch.setattr(
        module.requests,
        "get",
        fail_if_called,
    )

    collector._get_professor_statistics("Unknown Professor")


def test_get_professor_statistics_does_nothing_without_matching_anchor(
    monkeypatch,
    collector,
):
    professor = Professor(name="John Smith")
    collector._Collector__professors["John Smith"] = professor

    search_html = """
    <a
        class="TeacherCard__StyledTeacherCard-syjs0d-0 eerjaA"
        href="/professor/12345"
    >
        Jane Doe
    </a>
    """

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FakeResponse(search_html),
    )

    collector._get_professor_statistics("John Smith")

    assert professor.rating is None


def test_get_professor_statistics_propagates_http_error(
    monkeypatch,
    collector,
):
    professor = Professor(name="John Smith")
    collector._Collector__professors["John Smith"] = professor

    response = FakeResponse(
        error=requests.HTTPError("Search failed")
    )

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: response,
    )

    with pytest.raises(requests.HTTPError, match="Search failed"):
        collector._get_professor_statistics("John Smith")


def test_get_professor_data_returns_response(
    monkeypatch,
    collector,
):
    course = Course("CS", "151")

    request = Request(
        semester=Semester.FALL,
        year=2026,
        courses=[course],
    )

    professor = Professor(name="John Smith")
    collector._Collector__professors["John Smith"] = professor

    results = {
        course: [],
    }

    statistics_calls = []

    monkeypatch.setattr(
        collector,
        "_get_professors_per_course",
        lambda given_request: results,
    )

    monkeypatch.setattr(
        collector,
        "_get_professor_statistics",
        lambda name: statistics_calls.append(name),
    )

    response = collector.get_professor_data(request)

    assert response.request == request
    assert response.results == results
    assert statistics_calls == ["John Smith"]