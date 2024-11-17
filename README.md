# Project - Journey Plan 

## Introduction
This is my final project for CS50’s Introduction to Computer Science.

#### Video Demo:  <URL HERE>
#### Description:
Before traveling, planning the schedule is important for each person to use time effectively.
Journey Plan is a responsive website that is good for any device size.
This website is easy and clear to use, providing four main functions: creating, editing, deleting, and displaying the journey plan and daily schedule.

## Table of Contents
- [Introduction](#introduction)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)


## Technologies Used
The website was created using Flask in Python.
SQLite and SQLAlchemy are useful for setting up the database and querying it.
Jinja passes the database's information to HTML.
Some great interactive functions are built using JavaScript.
CSS and Bootstrap are simple for designing a responsive and well-designed website.

## Installation

set up the project locally.

1. Clone the repository:
   ```bash
   git clone https://github.com/wendy128516/cs50-project.git
   ```
2. Navigate into the project directory:
   ```bash
   cd fp
   ```
3. Install dependencies (if applicable):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

run the project

```bash
python app.py
flask run 
```

## Features
1. app.py 
- list all function code 

2. layout.html 
- display the layout
- 

3. plan.html 
- create journey plan

4. editPlan.html 
- edit journey plan with title, destination and date 

5. day.html 
- create daily schedule 

6. editDay.html 
- edit daily plan with time, location and activity

7. list.html 
- list out users' plans with time descending.
- select checkbox to delete plan 
- click title link to editPlan.html 
- click day link to editDay.html 

8. view.html 
- show the selected plan and daily schedule

9. other function with javascript 
- When you change the data, total day would be calculated automatically by between start date and end date
- When you change the time point, total time would be calculated automatically by between two time point 
- click the add/minus button to add/delete the row
