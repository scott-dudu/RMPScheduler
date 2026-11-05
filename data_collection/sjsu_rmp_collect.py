import requests
from bs4 import BeautifulSoup, Tag
from collections.abc import Iterable
from itertools import chain
from enum import Enum
from models import *


__SJSU_URL = 'https://www.sjsu.edu'
__SEM_PATH = '/classes/schedules/index.php'
__SJSU_RMP_URL = 'https://www.ratemyprofessors.com/search/professors/881?q='


class SemesterNotFoundError(Exception):
    """Exception raise when the semester is not found in the SJSU class schedule."""
    def __init__(self, message: str, semester: Semester, year: int):
        super().__init__(message)
        self.semester = semester
        self.year = year
        
    def __str__(self):
        return f'{self.args[0]}: {self.semester.value} {self.year}'


class CoursesNotFoundError(Exception):
    """Exception raise when the courses are not found in the SJSU class schedule for the given semester."""
    def __init__(self, message: str, courses: list[Course]):
        super().__init__(message)
        self.courses = courses
        
    def __str__(self):
        courses_text = '\n\t'.join([str(course) for course in self.courses])
        if courses_text:
            courses_text = f'\n\t{courses_text}'
        return f'{self.args[0]}:{courses_text}'
    

class Headers(Enum):
    SECTION = 'Section'
    MODE = 'Mode'
    DAYS = 'Days'
    TIME = 'Time'
    INSTRUCTOR = 'Instructor'

class Collector:
    def __init__(self):
        self.__professors = {}
    
    def _get_semester_url(self, semester: Semester, year: int) -> str:
        """
        Gets the URL for the given semester and year from the SJSU class schedule.
        
        Args:
            semester (Semester): The semester to validate.
            year (int): The year to validate.
            
        Returns:
            str: The URL for the given semester and year.

        Raises:
            SemesterNotFoundError: If the semester is not found in the SJSU class schedule.
            requests.HTTPError: If the HTTP request to the SJSU class schedule fails.
        """
        # Fetch the HTML content and raise an exception if the request fails.
        req = requests.get(f'{__SJSU_URL}{__SEM_PATH}')
        req.raise_for_status()
        
        # Parse the HTML content
        page = BeautifulSoup(req.text, 'html.parser')
        
        # Find the requested semester and year in the HTML content.
        str_to_find = f'{semester.value} {year}'
        semester_element = next(
            (
                item for item in page.find_all('li')
                if str_to_find in item.get_text(' ', strip=True)
            ),
            None
        )
        
        if semester_element is None:
            raise SemesterNotFoundError('Semester not found', semester, year)
        
        # Get the URL within the element
        link = semester_element.find('a')
        href = link.get('href') if link else None
        if href is None:
            raise SemesterNotFoundError('Semester has not been published', semester, year)
        
        # Return the URL for the given semester and year.
        return href


    def _parse_header(self, header: Iterable[Tag]) -> dict[str, int]:
        """
        Parses the header of the SJSU class schedule table to get the index of each relevant column.
        
        Args:
            header (Iterable[Tag]): An iterable of header elements from the SJSU class schedule table.
            
        Returns:
            dict[str, int]: A dictionary mapping each relevant column name to its index.
        """
        header_mapping = {}
        headers = [h.value for h in Headers]
        for index, item in enumerate(header):
            text = item.get_text(strip=True)
            for header_name in headers:
                if header_name in text:
                    header_mapping[header_name] = index
                    break
        return header_mapping


    def _parse_days(self, days_tag: Tag) -> list[Day]:
        """
        Parses the days string from the SJSU class schedule to get a list of Day enums.
        
        Args:
            days_tag (Tag): The days tag from the SJSU class schedule.
            
        Returns:
            list[Day]: A list of Day enums representing the days of the week for the class.
        """
        text = days_tag.get_text(strip=True)
        text = text.split('<br>') if '<br>' in text else list(text)
        return [Day(day.strip()) for day in text]


    def _normalize_time(self, time_str: str) -> str:
        """
        Normalizes the time string from the SJSU class schedule to HH:MM format.
        
        Args:
            time_str (str): The time string from the SJSU class schedule.
            
        Returns:
            str: The normalized time string in HH:MM format.
        """
        time_str = time_str.strip()
        if not time_str:
            return ""
        
        # Split the time into hours and minutes
        hours, minutes = time_str.split(':')
        
        # Normalize hours and minutes
        hours = int(hours)
        minutes = int(minutes)
        
        # Convert to 24-hour format if necessary
        if 'PM' in time_str.upper() and hours != 12:
            hours += 12
        elif 'AM' in time_str.upper() and hours == 12:
            hours = 0
        
        return f"{hours:02}:{minutes:02}"
    
    
    def _parse_time(self, time_tag: Tag) -> tuple[list[str], list[str]]:
        """
        Parses the time string from the SJSU class schedule to get the start and end times.
        
        Args:
            time_tag (Tag): The time tag from the SJSU class schedule.
            
        Returns:
            tuple[list[str], list[str]]: A tuple containing lists of the start and end times as strings in HH:MM format.
        """
        text = time_tag.get_text(strip=True)
        text = text.split('<br>') if '<br>' in text else [text]
        
        start_times = []
        end_times = []
        for time in text:
            if ':' not in time:
                continue # Skip invalid time formats
            start, end = time.split('-')
            start_times.append(self._normalize_time(start))
            end_times.append(self._normalize_time(end))
        
        return (start_times, end_times)


    def _parse_professors(self, professors_tag: Tag) -> list[Professor]:
        """
        Parses the professors string from the SJSU class schedule to get a list of Professor objects.
        
        Args:
            professors_tag (Tag): The professors tags from the SJSU class schedule.
            
        Returns:
            list[Professor]: A list of Professor objects representing the professors for the class.
        """
        pass


    def _get_sections(self, header: dict[str, int], course_elements: Iterable[Tag]) -> list[Section]:
        """
        Fetches the sections for the given course elements

        Args:
            header (dict[str, int]): A dictionary mapping each relevant column name to its index.
            course_elements (Iterable[Tag]): An iterable of course elements from the SJSU class schedule.
            
        Returns:
            list[Section]: A list of section objects for the given course elements.
        """
        sections = []
        for course in course_elements:
            course_data = course.find_all('td')
            
            # Get the section number, class time, and professors for the section of the course
            professors = self._parse_professors(course_data[header[Headers.INSTRUCTOR.value]])
            if not professors:
                continue  # Skip sections with no professors listed
            
            section_num = int(course_data[header[Headers.SECTION.value]].get_text(strip=True))
            mode = ClassMode(course_data[header[Headers.MODE.value]].get_text(strip=True))
            days = self._parse_days(course_data[header[Headers.DAYS.value]])
            start_time, end_time = self._parse_time(course_data[header[Headers.TIME.value]])
            
            class_time = ClassTime(
                mode=mode,
                days=days,
                start_time=start_time,
                end_time=end_time
            )

            section = Section(
                section_num=section_num,
                class_time=class_time,
                professors=professors
            )
            sections.append(section)

        return sections


    def _get_professors_per_course(self, request: Request) -> dict[Course, list[Section]]:
        """
        Fetches the professors for each course in the given request object.
        
        Args:
            request (Request): The request object containing the courses to fetch professors for.
            
        Returns:
            dict[Course, list[Section]]: A dictionary mapping each course to a list of section objects.

        Raises:
            SemesterNotFoundError: If the semester is not found in the SJSU class schedule.
            CoursesNotFoundError: If any of the courses are not found in the SJSU class schedule for the given semester.
            requests.HTTPError: If the HTTP request to the SJSU class schedule fails.
        """
        # Get the URL of the class schedules for the given semester and year.
        semester_url = self._get_semester_url(request.semester, request.year)
        classes_url = f'{__SJSU_URL}{semester_url}'

        # Courses to fetch professors for
        courses_to_fetch = request.courses
        courses_not_found = []
        sections = {}

        # Fetch the HTML content and raise an exception if the request fails.
        req = requests.get(classes_url)
        req.raise_for_status()

        # Parse the HTML content
        page = BeautifulSoup(req.text, 'html.parser')

        # Get the header mapping.
        header = self._parse_header(page.find_all('th'))

        # Find the courses in the HTML content and fetch the professors and times for each course.
        for course in courses_to_fetch:
            # Find the course in the HTML content
            str_to_find = str(course)
            course_elements = (
                item for item in page.find_all('tr')
                if str_to_find in item.get_text(' ', strip=True)
            )

            # Check if the course was found in the HTML content
            first_element = next(course_elements, None)
            if first_element is None:
                courses_not_found.append(course)
                continue

            # If a course was not found, do not process valid courses
            if courses_not_found:
                continue

            # Put the first element back into the generator to iterate over all elements
            course_elements = chain([first_element], course_elements)

            # Fetch the sections for the course
            course_sections = self._get_sections(header, course_elements)
            sections[course] = course_sections
        
        # If any courses were not found, raise an exception
        if courses_not_found:
            raise CoursesNotFoundError('Courses not found', courses_not_found)

        return sections


    def _get_professor(self, professor_url: str) -> Professor:
        """
        Fetches professor data from RateMyProfessors for the given professor URL.
        
        Args:
            professor_url (str): The URL of the professor's RateMyProfessors page.
            
        Returns:
            Professor: The professor object containing the fetched data.
        """
        pass


    def get_professor_data(self, request: Request) -> Response:
        """
        Fetches professor data from RateMyProfessors for the given request.
        
        Args:
            request (Request): The request object containing the search parameters.
        
        Returns:
            Response: The response object containing the fetched professor data.
        """
        pass