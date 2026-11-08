import pytest

from models import Course, Request, Semester
from sjsu_rmp_collect import Collector


@pytest.mark.six_courses
def test_spring_2027_six_courses_with_professor_data():
    collector = Collector()

    courses = [
        Course("CS", "146"),
        Course("CS", "147"),
        Course("CS", "151"),
        Course("CS", "152"),
        Course("CS", "154"),
        Course("CS", "156"),
    ]

    request = Request(
        semester=Semester.SPRING,
        year=2027,
        courses=courses,
    )

    response = collector.get_professor_data(request)

    assert response.request == request
    assert len(response.results) == 6

    print("\n" + "=" * 70)
    print("SPRING 2027 PROFESSOR RESULTS")
    print("=" * 70)

    for course, sections in response.results.items():
        print(f"\nCourse: {course}")
        print("-" * 70)

        # Prevent the same professor from being printed repeatedly
        professors = {}

        for section in sections:
            for professor in section.professors:
                key = professor.email or professor.name
                professors[key] = professor

        assert professors

        for professor in professors.values():
            rating = professor.rating

            if rating is None:
                rating_text = "No rating found"
            else:
                tags = ", ".join(sorted(rating.tags)) or "None"

                rating_text = (
                    f"Quality: {rating.quality}, "
                    f"Difficulty: {rating.difficulty}, "
                    f"Tags: {tags}"
                )

            print(f"Professor: {professor.name}")
            print(f"Email: {professor.email or 'N/A'}")
            print(f"Rating: {rating_text}")
            print()

    print("=" * 70)