import pytest
from bs4 import BeautifulSoup

import sjsu_rmp_collect as module
from models import ClassMode, Day, TimeBlock


@pytest.fixture
def parser():
    parser = module.Collector.__new__(module.Collector)

    # Needed because _parse_professors uses self.__professors.
    parser._Collector__professors = {}

    return parser


def make_tag(html):
    return BeautifulSoup(html, "html.parser").find()


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        (
            "<td>MW</td>",
            [Day.MONDAY, Day.WEDNESDAY],
        ),
        (
            "<td>M<br>W</td>",
            [Day.MONDAY, Day.WEDNESDAY],
        ),
        (
            "<td>T<br>R<br>F</td>",
            [Day.TUESDAY, Day.THURSDAY, Day.FRIDAY],
        ),
    ],
)
def test_parse_days(parser, html, expected):
    days_tag = make_tag(html)

    assert parser._parse_days(days_tag) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("09:00AM", "09:00"),
        ("10:15AM", "10:15"),
        ("12:00PM", "12:00"),
        ("01:30PM", "13:30"),
        ("12:30AM", "00:30"),
        ("09:00", "09:00"),
        ("", ""),
    ],
)
def test_normalize_time(parser, value, expected):
    assert parser._normalize_time(value) == expected


def test_parse_time(parser):
    time_tag = make_tag("<td>09:00AM-10:15AM</td>")

    result = parser._parse_time(time_tag)

    assert result == (
        ["09:00"],
        ["10:15"],
    )


def test_parse_time_with_multiple_ranges(parser):
    time_tag = make_tag(
        "<td>09:00AM-10:15AM 01:00PM-02:15PM</td>"
    )

    result = parser._parse_time(time_tag)

    assert result == (
        ["09:00", "13:00"],
        ["10:15", "14:15"],
    )


def test_parse_professors_with_anchor_tags(parser):
    professors_tag = make_tag(
        """
        <td>
            <a href="mailto:alice@example.com">Alice Smith</a>
            /
            <a href="mailto:bob@example.com">Bob Jones</a>
        </td>
        """
    )

    result = parser._parse_professors(professors_tag)

    assert [professor.name for professor in result] == [
        "Alice Smith",
        "Bob Jones",
    ]

    assert [professor.email for professor in result] == [
        "alice@example.com",
        "bob@example.com",
    ]


def test_parse_professors_without_anchor_tags(parser):
    professors_tag = make_tag(
        """
        <td>
            Alice Smith / Bob Jones
        </td>
        """
    )

    result = parser._parse_professors(professors_tag)

    assert [professor.name for professor in result] == [
        "Alice Smith",
        "Bob Jones",
    ]

    assert [professor.email for professor in result] == [
        None,
        None,
    ]


def test_parse_professors_reuses_existing_professor(parser):
    professors_tag = make_tag(
        """
        <td>
            <a href="mailto:alice@example.com">Alice Smith</a>
        </td>
        """
    )

    first_result = parser._parse_professors(professors_tag)
    second_result = parser._parse_professors(professors_tag)

    assert first_result[0] is second_result[0]
    assert len(parser._Collector__professors) == 1


@pytest.fixture
def collector():
    collector = module.Collector.__new__(module.Collector)
    collector._Collector__professors = {}
    return collector


HEADER = {
    module.Headers.SECTION.value: 0,
    module.Headers.MODE.value: 1,
    module.Headers.DAYS.value: 2,
    module.Headers.TIME.value: 3,
    module.Headers.INSTRUCTOR.value: 4,
}


def make_course_row(
    section="CS 151 (Section 01)",
    mode="In Person",
    days="MW",
    times="09:00AM-10:15AM",
    professor="Jane Smith",
):
    html = f"""
    <tr>
        <td>{section}</td>
        <td>{mode}</td>
        <td>{days}</td>
        <td>{times}</td>
        <td>
            <a href="mailto:jane@example.com">
                {professor}
            </a>
        </td>
    </tr>
    """

    return BeautifulSoup(html, "html.parser").find("tr")


def test_get_sections_includes_section_when_no_timeblock(collector):
    row = make_course_row()

    result = collector._get_sections(
        HEADER,
        [row],
        [],
    )

    assert len(result) == 1
    assert result[0].section_num == 1
    assert result[0].class_time.mode == ClassMode.IN_PERSON
    assert result[0].class_time.days == [
        Day.MONDAY,
        Day.WEDNESDAY,
    ]
    assert result[0].class_time.start_time == ["09:00"]
    assert result[0].class_time.end_time == ["10:15"]


def test_get_sections_skips_section_with_overlapping_timeblock(collector):
    row = make_course_row()

    timeblocks = [
        TimeBlock(
            day=Day.MONDAY,
            start_time="09:30",
            end_time="10:30",
        )
    ]

    result = collector._get_sections(
        HEADER,
        [row],
        timeblocks,
    )

    assert result == []


def test_get_sections_skips_section_when_timeblock_contains_class(
    collector,
):
    row = make_course_row()

    timeblocks = [
        TimeBlock(
            day=Day.MONDAY,
            start_time="08:00",
            end_time="11:00",
        )
    ]

    result = collector._get_sections(
        HEADER,
        [row],
        timeblocks,
    )

    assert result == []


def test_get_sections_keeps_section_for_different_day(collector):
    row = make_course_row()

    timeblocks = [
        TimeBlock(
            day=Day.TUESDAY,
            start_time="09:00",
            end_time="11:00",
        )
    ]

    result = collector._get_sections(
        HEADER,
        [row],
        timeblocks,
    )

    assert len(result) == 1
    assert result[0].section_num == 1


def test_get_sections_skips_section_when_timeblock_matches_end_boundary(
    collector,
):
    row = make_course_row()

    timeblocks = [
        TimeBlock(
            day=Day.WEDNESDAY,
            start_time="10:00",
            end_time="11:00",
        )
    ]

    result = collector._get_sections(
        HEADER,
        [row],
        timeblocks,
    )

    assert result == []