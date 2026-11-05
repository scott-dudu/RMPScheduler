from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Semester(Enum):
    FALL = "Fall"
    SPRING = "Spring"
    WINTER = "Winter"
    SUMMER = "Summer"
    
    
class Day(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class ClassMode(Enum):
    IN_PERSON = "In Person"
    ONLINE = "Online"
    HYBRID = "Hybrid"


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
    start_time: str='00:00'
    end_time: str='23:59'

    def __post_init__(self):
        if not isinstance(self.mode, ClassMode):
            raise TypeError(f"Mode must be a ClassMode enum, got: {type(self.mode)}")

        if not isinstance(self.days, list):
            raise TypeError(f"Days must be a list, got: {type(self.days)}")

        if not all(isinstance(day, Day) for day in self.days):
            raise TypeError("All items in days must be instances of Day enum")

        if not isinstance(self.start_time, str):
            raise TypeError(f"Start time must be a string, got: {type(self.start_time)}")

        if not isinstance(self.end_time, str):
            raise TypeError(f"End time must be a string, got: {type(self.end_time)}")


@dataclass
class Professor:
    name: str
    rating: float=0.0
    tags: dict[str, int]=field(default_factory=dict)
    class_times: list[ClassTime]=field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("Name must be a string")

        if not isinstance(self.rating, (int, float)):
            raise TypeError("Rating must be a number")

        if not 0 <= self.rating <= 5:
            raise ValueError(f"Rating must be between 0 and 5, got: {self.rating}")

        if not isinstance(self.tags, dict):
            raise TypeError("Tags must be a dictionary")

        if not all(
            isinstance(tag, str) and isinstance(count, int)
            for tag, count in self.tags.items()
        ):
            raise TypeError("Tags must contain str keys and int values")

        if not isinstance(self.class_times, list):
            raise TypeError("Class times must be a list")

        if not all(isinstance(time, ClassTime) for time in self.class_times):
            raise TypeError("Class times must contain only ClassTime objects")


@dataclass(frozen=True)
class Response:
    request: Request
    results: dict[Course, list[Professor]]

    def __post_init__(self):
        if not isinstance(self.request, Request):
            raise TypeError("Request must be a Request")

        if not isinstance(self.results, dict):
            raise TypeError("Results must be a dictionary")

        for course, professors in self.results.items():
            if not isinstance(course, Course):
                raise TypeError("Results keys must be Course objects")

            if not isinstance(professors, list):
                raise TypeError("Results values must be lists")

            if not all(isinstance(p, Professor) for p in professors):
                raise TypeError("Results values must contain only Professor objects")