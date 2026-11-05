import pytest

import sjsu_rmp_collect as module
from models import Course, Semester, Day, ClassMode, Professor, ClassTime, Request


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


HTML = """
<html>
    <body>
        <table>
            <thead>
                <tr>
                    <th class="all" width="10%" data-priority="1">
                        Section
                    </th>
                    <th>Class Number</th>
                    <th>Mode of Instruction</th>
                    <th class="all" data-priority="2">
                        Course Title
                    </th>
                    <th>Satisfies</th>
                    <th>Units</th>
                    <th>Type</th>
                    <th data-priority="3">Days</th>
                    <th data-priority="4">Times</th>
                    <th>Instructor</th>
                    <th>Location</th>
                    <th data-priority="3">Dates</th>
                    <th data-priority="2">Open Seats</th>
                    <th>Notes</th>
                </tr>
            </thead>

            <tbody>
                <tr>
                    <td>
                        <a>
                            AAS 1 (Section 01)
                        </a>
                    </td>
                    <td>47822</td>
                    <td>In Person</td>
                    <td>Introduction to Asian American Studies</td>
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
    </body>
</html>
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

def test_get_professors_per_course_returns_course_dictionary(monkeypatch):
    course = Course("AAS", "1")
    request = make_request([course])

    setup_successful_request(monkeypatch)

    result = module._get_professors_per_course(request)

    time = ClassTime(
        mode=ClassMode.IN_PERSON,
        days=[Day.MONDAY, Day.WEDNESDAY],
        start_time="09:00",
        end_time="10:15",
    )

    assert result == {
        course: [
            Professor(
                name="Test Name",
                class_times=[time],
            )
        ],
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