from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Semester(Enum):
    FALL = "Fall"
    SPRING = "Spring"
    WINTER = "Winter"
    SUMMER = "Summer"
    
    
class Day(Enum):
    MONDAY = "M"
    TUESDAY = "T"
    WEDNESDAY = "W"
    THURSDAY = "R"
    FRIDAY = "F"
    SATURDAY = "S"
    SUNDAY = "U"


class ClassMode(Enum):
    IN_PERSON = "in person"
    ONLINE = "online"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class Course:
    course_dept: str
    course_num: str

    def __post_init__(self):
        if not isinstance(self.course_dept, str):
            raise TypeError(f"Course department must be a string, got: {type(self.course_dept)}")

        if not self.course_dept.strip():
            raise ValueError("Course department cannot be empty")

        if not isinstance(self.course_num, str):
            raise TypeError(f"Course number must be a string, got: {type(self.course_num)}")

        if not self.course_num.strip():
            raise ValueError("Course number cannot be empty")
    
    def __str__(self):
        return f'{self.course_dept} {self.course_num}'


@dataclass(frozen=True)
class Request:
    semester: Semester | str
    year: int
    courses: list[Course]

    def __post_init__(self):
        # Validate year
        if not isinstance(self.year, int):
            raise TypeError(f"Year must be an integer, got: {type(self.year)}")

        current_year = datetime.now().year
        max_year = current_year + 1
        min_year = current_year - 1
        if not min_year <= self.year <= max_year:
            raise ValueError(f"Year must be between {min_year} and {max_year}, got: {self.year}")

        # Validate courses
        if not isinstance(self.courses, list):
            raise TypeError(f"Courses must be a list, got: {type(self.courses)}")

        max_courses = 8
        len_courses = len(self.courses)
        if not 1 <= len_courses <= max_courses:
            raise ValueError(f"Number of courses must be between 1 and {max_courses}, got: {len_courses}")

        if not all(isinstance(course, Course) for course in self.courses):
            raise TypeError("All items in courses must be instances of Course")

        # Validate semester
        if not isinstance(self.semester, Semester):
            if not isinstance(self.semester, str):
                raise TypeError(f"Semester must be a string or Semester enum, got: {type(self.semester)}")
            object.__setattr__(
                self,
                "semester",
                Semester(self.semester.capitalize())
            )


@dataclass(frozen=True)
class ClassTime:
    mode: ClassMode
    days: list[Day]
    start_time: list[str]
    end_time: list[str]

    def __post_init__(self):
        if not isinstance(self.mode, ClassMode):
            raise TypeError(f"Mode must be a ClassMode enum, got: {type(self.mode)}")

        if not isinstance(self.days, list):
            raise TypeError(f"Days must be a list, got: {type(self.days)}")

        if not all(isinstance(day, Day) for day in self.days):
            raise TypeError("All items in days must be instances of Day enum")

        if not isinstance(self.start_time, list):
            raise TypeError(f"Start time must be a list, got: {type(self.start_time)}")

        if not isinstance(self.end_time, list):
            raise TypeError(f"End time must be a list, got: {type(self.end_time)}")
        

@dataclass
class Section:
    section_num: int
    class_time: ClassTime
    professors: list[Professor]=field(default_factory=list)
    
    def __post_init__(self):
        if not isinstance(self.section_num, int):
            raise TypeError("Section number must be an integer")

        if not isinstance(self.class_time, ClassTime):
            raise TypeError("Class time must be a ClassTime object")

        if not isinstance(self.professors, list):
            raise TypeError("Professors must be a list")

        if not all(isinstance(professor, Professor) for professor in self.professors):
            raise TypeError("All items in professors must be instances of Professor")

@dataclass
class Professor:
    name: str
    email: str
    rating: Rating | None=None

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("Name must be a string")

        if not isinstance(self.email, str):
            raise TypeError("Email must be a string")

        if not isinstance(self.rating, Rating):
            raise TypeError("Rating must be a Rating object")


@dataclass
class Rating:
    quality: float
    difficulty: float
    top_reviews: list[str]=field(default_factory=list)
    least_reviews: list[str]=field(default_factory=list)
    tags: list[str]=field(default_factory=list)
    
    def __post_init__(self):
        if not isinstance(self.quality, float):
            raise TypeError("Quality must be a float")

        if not isinstance(self.difficulty, float):
            raise TypeError("Difficulty must be a float")

        if not isinstance(self.top_reviews, list):
            raise TypeError("Top reviews must be a list")

        if not all(isinstance(review, str) for review in self.top_reviews):
            raise TypeError("All items in top reviews must be strings")

        if not isinstance(self.least_reviews, list):
            raise TypeError("Least reviews must be a list")

        if not all(isinstance(review, str) for review in self.least_reviews):
            raise TypeError("All items in least reviews must be strings")

        if not isinstance(self.tags, list):
            raise TypeError("Tags must be a list")

        if not all(isinstance(tag, str) for tag in self.tags):
            raise TypeError("All items in tags must be strings")

@dataclass(frozen=True)
class Response:
    request: Request
    results: dict[Course, list[Section]]

    def __post_init__(self):
        if not isinstance(self.request, Request):
            raise TypeError("Request must be a Request")

        if not isinstance(self.results, dict):
            raise TypeError("Results must be a dictionary")

        for course, sections in self.results.items():
            if not isinstance(course, Course):
                raise TypeError("Results keys must be Course objects")

            if not isinstance(sections, list):
                raise TypeError("Results values must be lists")

            if not all(isinstance(s, Section) for s in sections):
                raise TypeError("Results values must contain only Section objects")