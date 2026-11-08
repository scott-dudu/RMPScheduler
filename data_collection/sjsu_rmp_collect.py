import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from collections.abc import Iterable
from enum import Enum
from models import *
from urllib.parse import quote, urljoin
from playwright.sync_api import sync_playwright


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


class SectionsNotFoundError(Exception):
    """Exception raise when there are no available sections after filtering with timeblocks"""
    def __init__(self, message:str, courses: list[Course]):
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
    __SJSU_URL = 'https://www.sjsu.edu'
    __SEM_PATH = '/classes/schedules/index.php'
    __SJSU_RMP_URL = 'https://www.ratemyprofessors.com/search/professors/881?q='
    
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
        url = urljoin(self.__SJSU_URL, self.__SEM_PATH)
        req = requests.get(url)
        req.raise_for_status()
        
        # Parse the HTML content
        page = BeautifulSoup(req.text, 'html.parser')
        
        # Find the requested semester and year in the HTML content.
        str_to_find = f'{semester.value} {year}'
        semester_element = next(
            (
                item for item in page.find_all('a')
                if str_to_find in item.get_text(' ', strip=True)
            ),
            None
        )
        
        if semester_element is None:
            raise SemesterNotFoundError('Semester not found', semester, year)
        
        # Get the URL within the element
        href = semester_element.get('href') if semester_element else None
        if href is None:
            raise SemesterNotFoundError('Semester has not been published', semester, year)
        
        # Return the URL for the given semester and year.
        return href


    def _parse_header(self, url: str) -> dict[str, int]:
        """
        Parses the header of the SJSU class schedule table to get the index of each relevant column.
        
        Args:
            url (str): A URL to the SJSU class schedule table.
            
        Returns:
            dict[str, int]: A dictionary mapping each relevant column name to its index.
        """
        req = requests.get(url)
        req.raise_for_status()
        
        page = BeautifulSoup(req.text, 'html.parser')
        header = page.find_all('th')
        
        header_mapping = {}
        for index, item in enumerate(header):
            text = item.get_text(strip=True)
            for header_name in Headers:
                if header_name.value in text:
                    header_mapping[header_name.value] = index
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
        text = days_tag.get_text('/', strip=True).upper().split('/')
        days = []
        for t in text:
            if (t == 'TBA'):
                days.append(t)
            else:
                days += list(t)
        
        day_mapping = {
            'M': Day.MONDAY,
            'T': Day.TUESDAY,
            'W': Day.WEDNESDAY,
            'R': Day.THURSDAY,
            'F': Day.FRIDAY,
            'S': Day.SATURDAY,
            'U': Day.SUNDAY,
            'TBA' : Day.TBA
        }
        
        return [day_mapping.get(day.strip()) for day in days]


    def _normalize_time(self, time_str: str) -> str:
        """
        Normalizes the time string from the SJSU class schedule to HH:MM format.
        
        Args:
            time_str (str): The time string from the SJSU class schedule.
            
        Returns:
            str: The normalized time string in HH:MM format.
        """
        time_str = time_str.strip().upper()
        if not time_str:
            return ""

        # Account for TBA times
        if time_str == 'TBA':
            return time_str
        
        # Split the time into hours and minutes
        hours, minutes = time_str.split(':')
        
        # Normalize hours and minutes
        hours = int(hours)
        minutes = int(minutes.removesuffix('AM').removesuffix('PM'))
        
        # Convert to 24-hour format if necessary
        if 'PM' in time_str and hours != 12:
            hours += 12
        elif 'AM' in time_str and hours == 12:
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
        text = time_tag.get_text(' ', strip=True).split()
        
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
        professors = []
        
        for child in professors_tag.children:
            if isinstance(child, Tag) and child.name == "a":
                name = child.get_text(" ", strip=True)
                href = child.get("href")

                email = (
                    href.removeprefix("mailto:")
                    if href
                    else None
                )

                professor_values = [(name, email)]

            elif isinstance(child, NavigableString):
                professor_values = [
                    (value.strip(), None)
                    for value in str(child).split("/")
                ]

            else:
                continue

            for name, email in professor_values:
                if not name or name.lower() == "tba":
                    continue

                if name not in self.__professors:
                    self.__professors[name] = Professor(
                        name=name,
                        email=email,
                    )

                professors.append(self.__professors[name])

        return professors


    def _get_sections(self, header: dict[str, int], course_elements: Iterable[Tag], timeblocks: list[TimeBlock]) -> list[Section]:
        """
        Fetches the sections for the given course elements

        Args:
            header (dict[str, int]): A dictionary mapping each relevant column name to its index.
            course_elements (Iterable[Tag]): An iterable of course elements from the SJSU class schedule.
            timeblocks (list[TimeBlock]): A list of time blocks where no classes should appear.

        Returns:
            list[Section]: A list of section objects for the given course elements.
        """
        sections = []
        for course in course_elements:
            course_data = course.find_all('td')

            # See if time of section violates time blocks
            start_times, end_times = self._parse_time(course_data[header[Headers.TIME.value]])
            days = self._parse_days(course_data[header[Headers.DAYS.value]])

            violates = any(
                timeblock.overlap(day, start, end)
                for timeblock in timeblocks
                for day in days
                for start, end in zip(start_times, end_times)
            )

            # If a time violates a timeblock, skip the section
            if violates:
                continue
            
            # Get the section number, class time, and professors for the section of the course
            professors = self._parse_professors(course_data[header[Headers.INSTRUCTOR.value]])
            if not professors:
                continue  # Skip sections with no professors listed
            
            section_num = course_data[header[Headers.SECTION.value]].get_text(strip=True)
            mode = ClassMode(course_data[header[Headers.MODE.value]].get_text(strip=True).lower())
            
            class_time = ClassTime(
                mode=mode,
                days=days,
                start_time=start_times,
                end_time=end_times
            )

            section_num = int(section_num.split()[-1].rstrip(')'))
            section = Section(
                section_num=section_num,
                class_time=class_time,
                professors=professors
            )
            sections.append(section)

        return sections


    def _find_classes(self, url: str, courses: list[Course]) -> dict[Course, list[Tag]]:
        """
        Uses Playwright to interact with the website and find all classes related to each course.

        Args:
            url (str): The URL that Playwright will use to search for classes.
            courses (list[Course]): The list of courses Playwright should search for.

        Returns:
            dict[Course, list[Tag]]: A dictionary mapping the requested course to all tags that contained the course name.

        Raises:
            CoursesNotFoundError: If any of the courses are not found in the SJSU class schedule for the given semester.
        """
        # To keep track of courses
        courses_not_found = []
        courses_found = {}

        # Start playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            
            try:
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")

                load_button = page.locator('#btnLoadTable')
                load_button.wait_for(state='visible')
                load_button.click()

                # Expand search size to reduce pagination overhead
                page.locator('select[name="classSchedule_length"]').select_option("100")
                page.wait_for_timeout(200)

                search_bar = page.get_by_role("searchbox")
                next_button = page.locator("#classSchedule_next")

                for course in courses:
                    tags = []
                    course_not_found = False

                    search_bar.fill(str(course))

                    # Give DataTables time to update the filtered rows.
                    page.wait_for_timeout(500)

                    while True:
                        rows = page.locator("#classSchedule tbody tr:visible")

                        # DataTables may use a visible empty row.
                        empty_message = page.locator("#classSchedule tbody td.dataTables_empty")
                        if empty_message.is_visible():
                            course_not_found = True
                            break

                        for row in rows.all():
                            row_html = row.evaluate("(element) => element.outerHTML")

                            soup = BeautifulSoup(row_html, "html.parser")
                            course_tag = soup.find("tr")

                            if course_tag is not None:
                                tags.append(course_tag)

                        # Check if there are more pages
                        classes = next_button.get_attribute("class") or ""
                        if "disabled" in classes:
                            break

                        previous_first_row = rows.first.inner_text()
                        next_button.click()
                        page.wait_for_function(
                            """
                            old_text => {
                                const row = document.querySelector(
                                    "#classSchedule tbody tr"
                                );
                                return row && row.innerText !== old_text;
                            }
                            """,
                            previous_first_row,
                        )

                    if course_not_found or not tags:
                        courses_not_found.append(course)
                    else:
                        courses_found[course] = tags

            finally:
                browser.close()

        if courses_not_found:
            raise CoursesNotFoundError("Courses not found", courses_not_found)

        return courses_found


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
            SectionsNotFoundError: If no sections for specific courses that fit time preferences.
            requests.HTTPError: If the HTTP request to the SJSU class schedule fails.
        """
        # Get the URL of the class schedules for the given semester and year.
        semester_url = self._get_semester_url(request.semester, request.year)
        classes_url = urljoin(self.__SJSU_URL, semester_url)
        
        # Get the header mapping.
        header = self._parse_header(classes_url)

        # Dictionary of course to list of sections
        sections = {}

        # Search for specific classes using playwright
        courses_to_fetch = self._find_classes(classes_url, request.courses)

        no_sections = []
        # Comb through the classes that were found
        for course in courses_to_fetch:
            course_elements = courses_to_fetch.get(course)
            course_sections = self._get_sections(header, course_elements, request.timeblocks)

            # If there are no available sections, add it to the error message
            if not course_sections:
                no_sections.append(course)

            # Do not add valid courses if an invalid one exists
            if no_sections:
                continue

            sections[course] = course_sections

        # Raise an exception if there was an invalid course
        if no_sections:
            raise SectionsNotFoundError('No sections found for these courses (maybe due to timeblocks)', no_sections)
        
        return sections


    def _get_professor_statistics(self, prof_obj: Professor, html: Tag) -> None:
        """
        Fetches statistics for a professor from RateMyProfessors.

        Args:
            prof_obj (Professor): The professor object that will get a Rating object.
            html (Tag): The HTML content that will be used to make the Rating object.
        """
        QUAL_DIV_CLASS = 'RatingValue__Numerator-qw8sqy-2 duhvlP'
        DIFF_DIV_CLASS = 'FeedbackItem__FeedbackNumber-uof32n-1 ecFgca'
        TAG_CLASS = 'Tag-bs9vf4-0 bmtbjB'

        # Get the overall rating
        quality = html.find('div', class_=QUAL_DIV_CLASS).get_text(strip=True).upper()
        if quality != 'N/A':
            quality = float(quality)

        # Get the difficulty rating
        difficulty = "N/A"
        for element in html.find_all("div", class_=DIFF_DIV_CLASS):
            parent_text = element.parent.get_text(" ",strip=True).lower()

            if "level of difficulty" in parent_text:
                raw_difficulty = element.get_text(strip=True)

                if not raw_difficulty.endswith("%"):
                    difficulty = float(raw_difficulty)

                break

        # Collect all tags with most recent reviews
        tags = {
            tag.get_text(strip=True).upper()
            for tag in html.find_all('span', class_=TAG_CLASS)
        }

        prof_obj.rating = Rating(
            quality=quality,
            difficulty=difficulty,
            tags=tags
        )


    def get_professor_data(self, request: Request) -> Response:
        """
        Fetches professor data from RateMyProfessors for the given request.
        
        Args:
            request (Request): The request object containing the search parameters.
        
        Returns:
            Response: The response object containing the fetched professor data.
        """
        result = self._get_professors_per_course(request)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            try:
                page = browser.new_page()

                for prof_name in self.__professors:
                    professor_url = f'{self.__SJSU_RMP_URL}{quote(prof_name)}'
                    page.goto(professor_url)

                    prof_obj = self.__professors.get(prof_name)

                    # Find the card of the professor on RMP
                    card = page.locator('a[href^="/professor/"]').first
                    if card.count() == 0:
                        prof_obj.rating = None
                        continue

                    # Get the link to actual professor page
                    href = card.get_attribute("href")
                    if href is None:
                        prof_obj.rating = None
                        None

                    # Go to the link
                    url = urljoin(self.__SJSU_RMP_URL, href)
                    page.goto(url)

                    # Get HTML content and use function to parse
                    main_locator = page.locator('main').first
                    main_locator.wait_for(state='visible')
                    main_html = main_locator.evaluate('(element) => element.outerHTML')
                    main_tag = BeautifulSoup(main_html, 'html.parser').find('main')

                    self._get_professor_statistics(prof_obj, main_tag)

            finally:
                browser.close()
        
        # for prof in self.__professors:
        #     self._get_professor_statistics(prof)
            
        return Response(
            request=request,
            results=result
        )