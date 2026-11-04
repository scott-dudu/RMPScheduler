import pytest

import sjsu_rmp_collect as module
from sjsu_rmp_collect import CoursesNotFoundError, _get_professors_per_course
from models import Course, Semester, Request


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


HTML = """
<table>
    <tbody>
        <tr>
            <td>
                <a>
                    CS 122 (Section 01)
                </a>
            </td>
            <td>47822</td>
            <td>In Person</td>
            <td>Advanced Python Programming</td>
            <td>GE: 6</td>
            <td>3.0</td>
            <td>LEC</td>
            <td>MW</td>
            <td>09:00AM-10:15AM</td>
            <td>
                <a>
                    Test Name
                </a>
            </td>
            <td>DMH227</td>
            <td>08/19/26-12/07/26</td>
            <td>0</td>
        </tr>
    </tbody>
</table>
"""


def make_request(courses):
    return Request(
        semester=Semester.FALL,
        year=2026,
        courses=courses,
    )


def setup_successful_request(monkeypatch):
    monkeypatch.setattr(
        module,
        "_get_semester_url",
        lambda semester, year: "/classes/fall2026",
    )

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FakeResponse(HTML),
    )


def test_get_professors_by_course_returns_course_dictionary(monkeypatch):
    course = Course("CS", "122")
    request = make_request([course])

    setup_successful_request(monkeypatch)

    result = module._get_professors_per_course(request)

    assert result == {
        course: {"Test Name"},
    }


def test_get_professors_by_course_raises_for_missing_course(monkeypatch):
    requested_course = Course("CS", "151")
    request = make_request([requested_course])

    setup_successful_request(monkeypatch)

    with pytest.raises(module.CoursesNotFoundError) as exception_info:
        module._get_professors_per_course(request)

    error = exception_info.value

    assert error.courses == [requested_course]


def test_get_professors_by_course_propagates_semester_error(monkeypatch):
    course = Course("CS", "122")
    request = make_request([course])

    def raise_error(semester, year):
        raise module.SemesterNotFoundError(
            "Semester not found",
            semester,
            year,
        )

    monkeypatch.setattr(
        module,
        "_get_semester_url",
        raise_error,
    )

    with pytest.raises(module.SemesterNotFoundError):
        module._get_professors_per_course(request)


def test_get_professors_by_course_propagates_http_error(monkeypatch):
    course = Course("CS", "122")
    request = make_request([course])

    class FailedResponse:
        text = ""

        def raise_for_status(self):
            raise module.requests.HTTPError("Request failed")

    monkeypatch.setattr(
        module,
        "_get_semester_url",
        lambda semester, year: "/classes/fall2026",
    )

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FailedResponse(),
    )

    with pytest.raises(module.requests.HTTPError, match="Request failed"):
        module._get_professors_per_course(request)