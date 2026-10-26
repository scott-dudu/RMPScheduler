from models import CourseRequest, SemesterRequest, Semester
from datetime import datetime


# -------------------------
# Valid input tests
# -------------------------

def test_valid_enum_semester():
    request = SemesterRequest(
        semester=Semester.FALL,
        year=datetime.now().year,
        courses=[
            CourseRequest("CS", "146")
        ]
    )

    assert request.semester == Semester.FALL


def test_valid_string_semester():
    request = SemesterRequest(
        semester="fall",
        year=datetime.now().year,
        courses=[
            CourseRequest("CS", "146")
        ]
    )

    assert request.semester == Semester.FALL


def test_valid_multiple_courses():
    request = SemesterRequest(
        semester="spring",
        year=datetime.now().year,
        courses=[
            CourseRequest("CS", "146"),
            CourseRequest("CS", "151"),
            CourseRequest("MATH", "161A")
        ]
    )

    assert len(request.courses) == 3


def test_max_courses():
    courses = [
        CourseRequest("CS", str(i))
        for i in range(8)
    ]

    request = SemesterRequest(
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
        SemesterRequest(
            semester="fall",
            year=current_year - 2,
            courses=[CourseRequest("CS", "146")]
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_year_too_far_future():
    current_year = datetime.now().year

    try:
        SemesterRequest(
            semester="fall",
            year=current_year + 2,
            courses=[CourseRequest("CS", "146")]
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


# -------------------------
# Invalid course tests
# -------------------------

def test_empty_courses():
    try:
        SemesterRequest(
            semester="fall",
            year=datetime.now().year,
            courses=[]
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_too_many_courses():
    courses = [
        CourseRequest("CS", str(i))
        for i in range(9)
    ]

    try:
        SemesterRequest(
            semester="fall",
            year=datetime.now().year,
            courses=courses
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_courses_not_list():
    try:
        SemesterRequest(
            semester="fall",
            year=datetime.now().year,
            courses="CS 146"
        )
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_invalid_object_in_courses():
    try:
        SemesterRequest(
            semester="fall",
            year=datetime.now().year,
            courses=[
                CourseRequest("CS", "146"),
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
        SemesterRequest(
            semester="autumn",
            year=datetime.now().year,
            courses=[CourseRequest("CS", "146")]
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_invalid_semester_type():
    try:
        SemesterRequest(
            semester=123,
            year=datetime.now().year,
            courses=[CourseRequest("CS", "146")]
        )
        assert False, "Expected TypeError"
    except TypeError:
        pass