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

    try:
        Request(
            semester="fall",
            year=current_year - 2,
            courses=[Course("CS", "146")]
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_year_too_far_future():
    current_year = datetime.now().year

    try:
        Request(
            semester="fall",
            year=current_year + 2,
            courses=[Course("CS", "146")]
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


# -------------------------
# Invalid course tests
# -------------------------

def test_empty_courses():
    try:
        Request(
            semester="fall",
            year=datetime.now().year,
            courses=[]
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_too_many_courses():
    courses = [
        Course("CS", str(i))
        for i in range(9)
    ]

    try:
        Request(
            semester="fall",
            year=datetime.now().year,
            courses=courses
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_courses_not_list():
    try:
        Request(
            semester="fall",
            year=datetime.now().year,
            courses="CS 146"
        )
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_invalid_object_in_courses():
    try:
        Request(
            semester="fall",
            year=datetime.now().year,
            courses=[
                Course("CS", "146"),
                "CS 151"
            ]
        )
        assert False, "Expected TypeError"
    except TypeError:
        pass


# -------------------------
# Invalid semester tests
# -------------------------

def test_invalid_semester_string():
    try:
        Request(
            semester="autumn",
            year=datetime.now().year,
            courses=[Course("CS", "146")]
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_invalid_semester_type():
    try:
        Request(
            semester=123,
            year=datetime.now().year,
            courses=[Course("CS", "146")]
        )
        assert False, "Expected TypeError"
    except TypeError:
        pass