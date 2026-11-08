import pytest
from bs4 import BeautifulSoup

import sjsu_rmp_collect as module
from models import ClassMode, Day


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