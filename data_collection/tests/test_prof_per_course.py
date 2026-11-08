import pytest

import sjsu_rmp_collect as module
from models import *


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
                    <th>Section</th>
                    <th>Class Number</th>
                    <th>Mode of Instruction</th>
                    <th>Course Title</th>
                    <th>Satisfies</th>
                    <th>Units</th>
                    <th>Type</th>
                    <th>Days</th>
                    <th>Times</th>
                    <th>Instructor</th>
                    <th>Location</th>
                    <th>Dates</th>
                    <th>Open Seats</th>
                    <th>Notes</th>
                </tr>
            </thead>

            <tbody>
                <tr>
                    <td>
                        <a>AAS 1 (Section 01)</a>
                    </td>
                    <td>47822</td>
                    <td>In Person</td>
                    <td>Introduction to Asian American Studies</td>
                    <td>GE: 6</td>
                    <td>3.0</td>
                    <td>LEC</td>
                    <td>MW</td>
                    <td>09:00-10:15</td>
                    <td>
                        <a>Test Name</a>
                    </td>
                    <td>DMH227</td>
                    <td>08/19/26-12/07/26</td>
                    <td>0</td>
                    <td></td>
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
        timeblocks=[]
    )


def setup_successful_request(monkeypatch, collector):
    monkeypatch.setattr(
        collector,
        "_get_semester_url",
        lambda semester, year: "/classes/fall2026",
    )

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FakeResponse(HTML),
    )


def test_get_professors_per_course_propagates_semester_error(
    monkeypatch,
):
    collector = module.Collector()
    course = Course("AAS", "1")
    request = make_request([course])

    def raise_error(semester, year):
        raise module.SemesterNotFoundError(
            "Semester not found",
            semester,
            year,
        )

    monkeypatch.setattr(
        collector,
        "_get_semester_url",
        raise_error,
    )

    with pytest.raises(module.SemesterNotFoundError):
        collector._get_professors_per_course(request)


def test_get_professors_per_course_propagates_http_error(
    monkeypatch,
):
    collector = module.Collector()
    course = Course("AAS", "1")
    request = make_request([course])

    class FailedResponse:
        text = ""

        def raise_for_status(self):
            raise module.requests.HTTPError("Request failed")

    monkeypatch.setattr(
        collector,
        "_get_semester_url",
        lambda semester, year: "/classes/fall2026",
    )

    monkeypatch.setattr(
        module.requests,
        "get",
        lambda url: FailedResponse(),
    )

    with pytest.raises(
        module.requests.HTTPError,
        match="Request failed",
    ):
        collector._get_professors_per_course(request)