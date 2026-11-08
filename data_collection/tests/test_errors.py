import pytest
from models import Semester, Course
from sjsu_rmp_collect import SemesterNotFoundError, CoursesNotFoundError, SectionsNotFoundError


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
        "\tCS 151\n"
        "\tCS 157A"
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
    assert str(error) == "Courses not found:\n\tCS 160"


def test_sections_not_found_error_stores_courses():
    courses = [
        Course("CS", "146"),
        Course("CS", "151"),
    ]

    error = SectionsNotFoundError(
        "No sections found",
        courses,
    )

    assert error.args == ("No sections found",)
    assert error.courses == courses


def test_sections_not_found_error_string():
    courses = [
        Course("CS", "146"),
        Course("CS", "151"),
    ]

    error = SectionsNotFoundError(
        "No sections found",
        courses,
    )

    expected = (
        "No sections found:\n"
        "\tCS 146\n"
        "\tCS 151"
    )

    assert str(error) == expected


def test_sections_not_found_error_with_no_courses():
    error = SectionsNotFoundError(
        "No sections found",
        [],
    )

    assert str(error) == "No sections found:"


def test_sections_not_found_error_can_be_raised():
    course = Course("CS", "146")

    with pytest.raises(SectionsNotFoundError) as exception_info:
        raise SectionsNotFoundError(
            "No sections found",
            [course],
        )

    error = exception_info.value

    assert error.courses == [course]
    assert str(error) == (
        "No sections found:\n"
        "\tCS 146"
    )