import pytest
from models import Course, Request, Semester
from datetime import datetime


# -------------------------
# Valid input tests
# -------------------------

def test_valid_enum_semester():
    request = Request(
        semester=Semester.FALL,
        year=datetime.now().year,
        courses=[
            Course("CS", "146")
        ]
    )

    assert request.semester == Semester.FALL


def test_valid_string_semester():
    request = Request(
        semester="fall",
        year=datetime.now().year,
        courses=[
            Course("CS", "146")
        ]
    )

    assert request.semester == Semester.FALL


def test_valid_multiple_courses():
    request = Request(
        semester="spring",
        year=datetime.now().year,
        courses=[
            Course("CS", "146"),
            Course("CS", "151"),
            Course("MATH", "161A")
        ]
    )

    assert len(request.courses) == 3


def test_max_courses():
    courses = [
        Course("CS", str(i))
        for i in range(8)
    ]

    request = Request(
        semester="summer",
        year=datetime.now().year,
        courses=courses
    )

    assert len(request.courses) == 8


# -------------------------
# Invalid year tests
# -------------------------

def test_year_too_old():
    current_year = datetime.now().year

    with pytest.raises(ValueError):
        Request(
            semester="fall",
            year=current_year - 2,
            courses=[Course("CS", "146")]
        )


def test_year_too_far_future():
    current_year = datetime.now().year

    with pytest.raises(ValueError):
        Request(
            semester="fall",
            year=current_year + 2,
            courses=[Course("CS", "146")]
        )


# -------------------------
# Invalid course tests
# -------------------------

def test_empty_courses():
    with pytest.raises(ValueError):
        Request(
            semester="fall",
            year=datetime.now().year,
            courses=[]
        )


def test_too_many_courses():
    courses = [
        Course("CS", str(i))
        for i in range(9)
    ]

    with pytest.raises(ValueError):
        Request(
            semester="fall",
            year=datetime.now().year,
            courses=courses
        )


def test_courses_not_list():
    with pytest.raises(TypeError):
        Request(
            semester="fall",
            year=datetime.now().year,
            courses="CS 146"
        )


def test_invalid_object_in_courses():
    with pytest.raises(TypeError):
        Request(
            semester="fall",
            year=datetime.now().year,
            courses=[
                Course("CS", "146"),
                "CS 151"
            ]
        )


def test_course_with_empty_department():
    with pytest.raises(ValueError):
        Course("", "146")


def test_course_with_empty_number():
    with pytest.raises(ValueError):
        Course("CS", "")


def test_course_with_non_string_department():
    with pytest.raises(TypeError):
        Course(123, "146")


def test_course_with_non_string_number():
    with pytest.raises(TypeError):
        Course("CS", 146)


# -------------------------
# Invalid semester tests
# -------------------------

def test_invalid_semester_string():
    with pytest.raises(ValueError):
        Request(
            semester="autumn",
            year=datetime.now().year,
            courses=[Course("CS", "146")]
        )


def test_invalid_semester_type():
    with pytest.raises(TypeError):
        Request(
            semester=123,
            year=datetime.now().year,
            courses=[Course("CS", "146")]
        )