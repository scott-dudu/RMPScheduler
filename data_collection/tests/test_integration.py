import pytest

from models import Course, Request, Semester
from sjsu_rmp_collect import Collector, CoursesNotFoundError, Headers


SPRING_2027_URL = "https://www.sjsu.edu/classes/schedules/spring-2027.php"


def make_request(course):
    return Request(
        semester=Semester.SPRING,
        year=2027,
        courses=[course],
    )


@pytest.mark.integration
def test_spring_2027_url_exists():
    collector = Collector()

    result = collector._get_semester_url(
        Semester.SPRING,
        2027,
    )

    assert "spring-2027.php" in result.lower()


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

    with pytest.raises(CoursesNotFoundError) as exception_info:
        collector._get_professors_per_course(
            make_request(course)
        )

    assert exception_info.value.courses == [course]


@pytest.mark.integration
def test_spring_2027_cs151_is_parsed():
    collector = Collector()
    course = Course("CS", "151")

    result = collector._get_professors_per_course(
        make_request(course)
    )

    assert course in result
    assert result[course]

    for section in result[course]:
        assert section.section_num > 0
        assert section.professors
        assert section.class_time.days
        assert section.class_time.start_time
        assert section.class_time.end_time


@pytest.mark.rmp_integration
def test_cs151_professor_data_is_returned():
    collector = Collector()
    course = Course("CS", "151")
    request = make_request(course)

    response = collector.get_professor_data(request)

    assert response.request == request
    assert course in response.results
    assert response.results[course]

    professors = {}

    for section in response.results[course]:
        for professor in section.professors:
            professors[professor.name] = professor

    assert professors

    print("\n" + "=" * 60)
    print("CS 151 PROFESSOR DATA")
    print("=" * 60)

    for professor in professors.values():
        if professor.rating is None:
            quality = "N/A"
            difficulty = "N/A"
            tags = "N/A"
        else:
            quality = professor.rating.quality
            difficulty = professor.rating.difficulty
            tags = ", ".join(sorted(professor.rating.tags)) or "None"

        print(f"\nProfessor: {professor.name}")
        print(f"Email: {professor.email or 'N/A'}")
        print(f"Quality: {quality}")
        print(f"Difficulty: {difficulty}")
        print(f"Tags: {tags}")