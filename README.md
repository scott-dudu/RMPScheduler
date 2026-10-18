# RMPScheduler@SJSU

Authors: Scott Du and Karma Balakrishnan

## Project Description

RMPScheduler@SJSU is a website that takes the user's preferred classes for next semester and uses ratings from ratemyprofessors.com to generate a schedule of the user's choosing. The website will use San Jose State University's class schedule to see which professors are teaching the requested classes. Using reviews from ratemyprofessors.com, the website will rank the best matched professors to take. The website will then generate a variety of different schedules based on times, professor ratings, and tags. Users can select their preferences on what tags professors were assigned. In addition, the generated schedules will give a small description of each professor and how many reviews they have.

## Project Outline

- The website will be a stateless interface where the user can input their preferred classes, categories, and time blocks. 

- On the left side of the website, there will be a class list for the user to input. For each class, the user will need to give the class subject and class code. There will be buttons to add more or delete classes from the current list. The maximum allowed number of classes will be 8. If the class does not exist, a warning will be given stating that the requested class is not offered. 

- On the right side of the website, there will be a preferences column where the user can choose their preferred semester, add which tags they want the professors to have or avoid, and any time blocks where they cannot make it. 

- On the bottom, there will be a submit button, which the user will click to generate the schedules.

- To display the schedules, it will generate the schedules as a list containing information like the class name, time, professor, open seats, and room.

### Data Collection and Storage Plan (Scott Du)

- Webscraping packages : Requests and BeautifulSoup
- Check which semester schedules are available by link and store it.
- After the user inputs their classes, scrape the class schedule itself and find the available professors. If the class does not exist, throw an error.
- Search on rate my professor for that specific professor in sjsu.
  - Grab their rating, the amount of reviews, and compile the tags.

### Data Analysis and Visualization Plan (Karma Balakrishnan)

- Flask (subject to change) to create website
- First remove, any classes that do not work with the user's time blocks.
- Remove any professors with undesired tags.
- Find the highest rated professor of all the given professors, choose the class time with the least interferences with other classes.
- If the user requested multiple schedules, start with a different class.
- Redirect to another page, and display the schedules as lists. Provide a small description of each professor and how many reviews they have.
