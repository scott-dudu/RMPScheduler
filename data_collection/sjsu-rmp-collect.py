import requests
from models import Request, Response, Semester, Course, Professor


__SJSU_CLASS_URL = 'https://www.sjsu.edu/classes/schedules/index.php'
__SJSU_RMP_URL = 'https://www.ratemyprofessors.com/search/professors/881?q='


class SemesterNotFoundError(Exception):
    """Exception raise when the semester is not found in the SJSU class schedule."""
    pass


class CoursesNotFoundError(Exception):
    """Exception raise when the courses are not found in the SJSU class schedule for the given semester."""
    pass


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
    """
    pass


def _check_valid_request(request: Request) -> None:
    """
    Validates the given request object to see if the semester and courses are available.
    
    Args:
        request (Request): The request object to validate.
        
    Raises:
        CoursesNotFoundError: If any of the courses are not found in the SJSU class schedule for the given semester.
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