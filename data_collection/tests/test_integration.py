import pytest

from models import Course, Request, Semester
from sjsu_rmp_collect import Collector, CoursesNotFoundError, Headers


SPRING_2027_URL = "https://www.sjsu.edu/classes/schedules/spring-2027.php"


@pytest.mark.integration
def test_spring_2027_url_exists():
    collector = Collector()

    result = collector._get_semester_url(
        Semester.SPRING,
        2027,
    )

    assert "/classes/schedules/spring-2027.php" in result.lower()


@pytest.mark.integration
def test_parse_header():
    collector = Collector()
    result = collector._parse_header(SPRING_2027_URL)

    assert result[Headers.SECTION.value] == 0
    assert result[Headers.MODE.value] == 2
    assert result[Headers.DAYS.value] == 7
    assert result[Headers.TIME.value] == 8
    assert result[Headers.INSTRUCTOR.value] == 9


@pytest.mark.integration
def test_cs49c_is_not_found_in_spring_2027():
    collector = Collector()

    course = Course("CS", "49C")

    request = Request(
        semester=Semester.SPRING,
        year=2027,
        courses=[course],
    )

    with pytest.raises(CoursesNotFoundError) as exception_info:
        collector._get_professors_per_course(request)

    assert exception_info.value.courses == [course]


@pytest.mark.integration
def test_spring_2027_cs151_is_parsed():
    collector = Collector()

    course = Course("CS", "151")

    request = Request(
        semester=Semester.SPRING,
        year=2027,
        courses=[course],
    )

    result = collector._get_professors_per_course(request)

    assert course in result
    assert len(result[course]) > 0

    sections = result[course]

    assert all(section.section_num > 0 for section in sections)
    assert all(section.professors for section in sections)

    professor_names = {
        professor.name
        for section in sections
        for professor in section.professors
    }

    assert "Suneuy Kim" in professor_names