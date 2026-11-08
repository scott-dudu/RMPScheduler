import pytest
from bs4 import BeautifulSoup

from models import Professor
from sjsu_rmp_collect import Collector


@pytest.fixture
def collector():
    return Collector()


def make_tag(html: str):
    return BeautifulSoup(html, "html.parser").find("main")


def test_get_professor_statistics_updates_professor_rating(collector):
    professor = Professor(
        name="John Smith",
        email="john@example.com",
    )

    html = """
    <main>
        <div class="RatingValue__Numerator-qw8sqy-2 duhvlP">
            4.5
        </div>

        <div class="FeedbackItem__FeedbackNumber-uof32n-1 ecFgca">
            2.8
        </div>

        <span class="Tag-bs9vf4-0 bmtbjB">
            Tough grader
        </span>

        <span class="Tag-bs9vf4-0 bmtbjB">
            Extra credit
        </span>
    </main>
    """

    collector._get_professor_statistics(
        professor,
        make_tag(html),
    )

    assert professor.rating is not None
    assert professor.rating.quality == 4.5
    assert professor.rating.difficulty == 2.8
    assert professor.rating.tags == {
        "TOUGH GRADER",
        "EXTRA CREDIT",
    }


def test_get_professor_statistics_handles_missing_difficulty(collector):
    professor = Professor(name="John Smith")

    html = """
    <main>
        <div class="RatingValue__Numerator-qw8sqy-2 duhvlP">
            4.0
        </div>
    </main>
    """

    collector._get_professor_statistics(
        professor,
        make_tag(html),
    )

    assert professor.rating.quality == 4.0
    assert professor.rating.difficulty == "N/A"
    assert professor.rating.tags == set()


def test_get_professor_statistics_handles_na_values(collector):
    professor = Professor(name="John Smith")

    html = """
    <main>
        <div class="RatingValue__Numerator-qw8sqy-2 duhvlP">
            N/A
        </div>

        <div class="FeedbackItem__FeedbackNumber-uof32n-1 ecFgca">
            N/A
        </div>
    </main>
    """

    collector._get_professor_statistics(
        professor,
        make_tag(html),
    )

    assert professor.rating.quality == "N/A"
    assert professor.rating.difficulty == "N/A"
    assert professor.rating.tags == set()


def test_get_professor_statistics_collects_duplicate_tags_once(collector):
    professor = Professor(name="John Smith")

    html = """
    <main>
        <div class="RatingValue__Numerator-qw8sqy-2 duhvlP">
            4.2
        </div>

        <span class="Tag-bs9vf4-0 bmtbjB">Helpful</span>
        <span class="Tag-bs9vf4-0 bmtbjB">Helpful</span>
    </main>
    """

    collector._get_professor_statistics(
        professor,
        make_tag(html),
    )

    assert professor.rating.tags == {"HELPFUL"}