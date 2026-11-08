import pytest
from datetime import datetime

from models import Course, Day, Request, Semester, TimeBlock


CURRENT_YEAR = datetime.now().year


def valid_timeblocks():
    return [TimeBlock(Day.MONDAY, "09:00", "10:15")]


def valid_courses():
    return [Course("CS", "146")]


# -------------------------
# TimeBlock tests
# -------------------------

def test_valid_timeblock():
    timeblock = TimeBlock(Day.MONDAY, "09:00", "17:30")

    assert timeblock.day == Day.MONDAY
    assert timeblock.start_time == "09:00"
    assert timeblock.end_time == "17:30"


@pytest.mark.parametrize(
    "start_time,end_time",
    [
        ("00:00", "23:59"),
        ("12:00", "13:30"),
        ("09:05", "09:45"),
    ],
)
def test_valid_24_hour_times(start_time, end_time):
    TimeBlock(Day.TUESDAY, start_time, end_time)


@pytest.mark.parametrize(
    "start_time,end_time",
    [
        ("9:00", "10:00"),
        ("24:00", "10:00"),
        ("10:00", "24:00"),
        ("10:60", "11:00"),
        ("10:00 AM", "11:00"),
        ("", "11:00"),
    ],
)
def test_invalid_time_format(start_time, end_time):
    with pytest.raises(ValueError, match="Expected HH:MM"):
        TimeBlock(Day.WEDNESDAY, start_time, end_time)


def test_tba_day_is_invalid():
    with pytest.raises(
        ValueError,
        match="Time block cannot be for a TBA day",
    ):
        TimeBlock(Day.TBA, "09:00", "10:00")


def test_invalid_day_type():
    with pytest.raises(TypeError, match="Day must be of type Day"):
        TimeBlock("Monday", "09:00", "10:00")


def test_non_string_start_time():
    with pytest.raises(TypeError, match="Start time must be a string"):
        TimeBlock(Day.MONDAY, 900, "10:00")


def test_non_string_end_time():
    with pytest.raises(TypeError, match="End time must be a string"):
        TimeBlock(Day.MONDAY, "09:00", 1000)


def test_timeblock_overlap_on_same_day():
    timeblock = TimeBlock(Day.MONDAY, "09:00", "10:00")

    assert timeblock.overlap(Day.MONDAY, "09:30", "10:30")


def test_timeblock_does_not_overlap_on_different_day():
    timeblock = TimeBlock(Day.MONDAY, "09:00", "10:00")

    assert not timeblock.overlap(Day.TUESDAY, "09:30", "10:30")


# -------------------------
# Valid Request tests
# -------------------------

def test_valid_enum_semester():
    request = Request(
        semester=Semester.FALL,
        year=CURRENT_YEAR,
        courses=valid_courses(),
        timeblocks=valid_timeblocks(),
    )

    assert request.semester == Semester.FALL
    assert request.timeblocks == valid_timeblocks()


def test_valid_string_semester():
    request = Request(
        semester="fall",
        year=CURRENT_YEAR,
        courses=valid_courses(),
        timeblocks=valid_timeblocks(),
    )

    assert request.semester == Semester.FALL


def test_valid_multiple_courses():
    courses = [
        Course("CS", "146"),
        Course("CS", "151"),
        Course("MATH", "161A"),
    ]

    request = Request(
        semester="spring",
        year=CURRENT_YEAR,
        courses=courses,
        timeblocks=valid_timeblocks(),
    )

    assert len(request.courses) == 3


def test_max_courses():
    courses = [
        Course("CS", str(i))
        for i in range(8)
    ]

    request = Request(
        semester="summer",
        year=CURRENT_YEAR,
        courses=courses,
        timeblocks=valid_timeblocks(),
    )

    assert len(request.courses) == 8


def test_empty_timeblocks_are_allowed():
    request = Request(
        semester="fall",
        year=CURRENT_YEAR,
        courses=valid_courses(),
        timeblocks=[],
    )

    assert request.timeblocks == []


# -------------------------
# Invalid year tests
# -------------------------

def test_year_too_old():
    with pytest.raises(ValueError):
        Request(
            semester="fall",
            year=CURRENT_YEAR - 2,
            courses=valid_courses(),
            timeblocks=valid_timeblocks(),
        )


def test_year_too_far_future():
    with pytest.raises(ValueError):
        Request(
            semester="fall",
            year=CURRENT_YEAR + 2,
            courses=valid_courses(),
            timeblocks=valid_timeblocks(),
        )


# -------------------------
# Invalid course tests
# -------------------------

def test_empty_courses():
    with pytest.raises(ValueError):
        Request(
            semester="fall",
            year=CURRENT_YEAR,
            courses=[],
            timeblocks=valid_timeblocks(),
        )


def test_too_many_courses():
    courses = [
        Course("CS", str(i))
        for i in range(9)
    ]

    with pytest.raises(ValueError):
        Request(
            semester="fall",
            year=CURRENT_YEAR,
            courses=courses,
            timeblocks=valid_timeblocks(),
        )


def test_courses_not_list():
    with pytest.raises(TypeError):
        Request(
            semester="fall",
            year=CURRENT_YEAR,
            courses="CS 146",
            timeblocks=valid_timeblocks(),
        )


def test_invalid_object_in_courses():
    with pytest.raises(TypeError):
        Request(
            semester="fall",
            year=CURRENT_YEAR,
            courses=[
                Course("CS", "146"),
                "CS 151",
            ],
            timeblocks=valid_timeblocks(),
        )


# -------------------------
# Invalid timeblocks tests
# -------------------------

def test_timeblocks_not_list():
    with pytest.raises(
        TypeError,
        match="Time blocks must be a list",
    ):
        Request(
            semester="fall",
            year=CURRENT_YEAR,
            courses=valid_courses(),
            timeblocks=TimeBlock(Day.MONDAY, "09:00", "10:00"),
        )


def test_invalid_object_in_timeblocks():
    with pytest.raises(
        TypeError,
        match="All items in timeblocks",
    ):
        Request(
            semester="fall",
            year=CURRENT_YEAR,
            courses=valid_courses(),
            timeblocks=["09:00-10:00"],
        )


# -------------------------
# Invalid semester tests
# -------------------------

def test_invalid_semester_string():
    with pytest.raises(ValueError):
        Request(
            semester="autumn",
            year=CURRENT_YEAR,
            courses=valid_courses(),
            timeblocks=valid_timeblocks(),
        )


def test_invalid_semester_type():
    with pytest.raises(TypeError):
        Request(
            semester=123,
            year=CURRENT_YEAR,
            courses=valid_courses(),
            timeblocks=valid_timeblocks(),
        )