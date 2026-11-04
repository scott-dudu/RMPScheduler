import requests
from bs4 import BeautifulSoup
from models import Request, Response, Semester, Course, Professor


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


def _get_semester_url(semester: Semester, year: int) -> str:
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


def _get_professors_per_course(request: Request) -> dict[Course, list[Professor]]:
    """
    Fetches the professors for each course in the given request object.
    
    Args:
        request (Request): The request object containing the courses to fetch professors for.
        
    Returns:
        dict[Course, list[Professor]]: A dictionary mapping each course to a list of professors.

    Raises:
        SemesterNotFoundError: If the semester is not found in the SJSU class schedule.
        CoursesNotFoundError: If any of the courses are not found in the SJSU class schedule for the given semester.
        requests.HTTPError: If the HTTP request to the SJSU class schedule fails.
    """
    pass


def _get_professor(professor_url: str) -> Professor:
    """
    Fetches professor data from RateMyProfessors for the given professor URL.
    
    Args:
        professor_url (str): The URL of the professor's RateMyProfessors page.
        
    Returns:
        Professor: The professor object containing the fetched data.
    """
    pass


def get_professor_data(request: Request) -> Response:
    """
    Fetches professor data from RateMyProfessors for the given request.
    
    Args:
        request (Request): The request object containing the search parameters.
    
    Returns:
        Response: The response object containing the fetched professor data.
    """
    pass