import pytest
from models import Semester, Course
from sjsu_rmp_collect import SemesterNotFoundError, CoursesNotFoundError


def test_semester_not_found_error_stores_attributes():
    error = SemesterNotFoundError(
        "Semester not found",
        Semester.FALL,
        2026,
    )

    assert error.args == ("Semester not found",)
    assert error.semester == Semester.FALL
    assert error.year == 2026


def test_semester_not_found_error_string():
    error = SemesterNotFoundError(
        "Semester not found",
        Semester.FALL,
        2026,
    )

    assert str(error) == "Semester not found: Fall 2026"


def test_semester_not_found_error_can_be_raised():
    with pytest.raises(SemesterNotFoundError) as exception_info:
        raise SemesterNotFoundError(
            "Semester not found",
            Semester.SPRING,
            2027,
        )

    error = exception_info.value

    assert error.semester == Semester.SPRING
    assert error.year == 2027
    assert str(error) == "Semester not found: Spring 2027"


def test_courses_not_found_error_stores_courses():
    courses = [
        Course('CS', '122'),
        Course('CS', '146'),
    ]

    error = CoursesNotFoundError("Courses not found", courses)

    assert error.args == ("Courses not found",)
    assert error.courses == courses


def test_courses_not_found_error_string():
    courses = [
        Course('CS', '151'),
        Course('CS', '157A'),
    ]

    error = CoursesNotFoundError("Courses not found", courses)

    expected = (
        "Courses not found:\n"
        "\tCS-151\n"
        "\tCS-157A"
    )

    assert str(error) == expected


def test_courses_not_found_error_with_no_courses():
    error = CoursesNotFoundError("Courses not found", [])

    assert str(error) == "Courses not found:"


def test_courses_not_found_error_can_be_raised():
    courses = [Course('CS', '160')]

    with pytest.raises(CoursesNotFoundError) as exception_info:
        raise CoursesNotFoundError("Courses not found", courses)

    error = exception_info.value

    assert error.courses == courses
    assert str(error) == "Courses not found:\n\tCS-160"