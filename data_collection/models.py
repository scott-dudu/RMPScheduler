from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Semester(Enum):
    FALL = "Fall"
    SPRING = "Spring"
    WINTER = "Winter"
    SUMMER = "Summer"

@dataclass
class CourseRequest:
    course_dept: str
    course_num: str

@dataclass
class SemesterRequest:
    semester: Semester
    year: int
    courses: list[CourseRequest]

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

        if not all(isinstance(course, CourseRequest) for course in self.courses):
            raise TypeError("All items in courses must be instances of CourseRequest")

        # Validate semester
        if not isinstance(self.semester, Semester):
            if not isinstance(self.semester, str):
                raise TypeError(f"Semester must be a string or Semester enum, got: {type(self.semester)}")
            self.semester = Semester(self.semester.capitalize())