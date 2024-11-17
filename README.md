# Project - Journey Plan 

## Introduction
This is my final project for CS50’s Introduction to Computer Science.

#### Video Demo:  [Journey Plan ](https://youtu.be/XnJ86OmLDsk)
#### Description:
Planning the schedule is important for each person before traveling. 
Well-planned trips can make you happier and more meaningful during your journey. 
Journey Plan is a responsive website that is good for any device size.
You can create, edit, delete, and display the plan and daily schedule.
This website can easily manage and track your activities for each day of your trip, ensuring you make the most of your time.

In order to make the user-friendly website, I used session saving "dayCount". 
When a new plan is built, the website is navigated to day.html. 
When each "POST" is requested, "dayCount" is re-calculated and then the number is passed to "GET" in day.html until "remainingDay" is less than 0. If all data input is finished, the website will navigate to list.html.

Display the related code:
```
@app.route("/day", methods=["GET", "POST"])
def day():
    # the latest plan
    users_id = session["user_id"]
    record = db.session.execute(text("SELECT * FROM plan WHERE users_id = :users_id ORDER BY created_at DESC"),{'users_id': users_id}).fetchone()
    db.session.commit()

    # daily format
    if request.method == "GET":
        if 'dayCount' not in session:
            session['dayCount'] = 1
        dayCount = session['dayCount']
        totalDay = record[6]
        remainingDay = totalDay - dayCount
        if remainingDay == 0:
            return render_template('day.html', record=record, dayCount=dayCount, button="Save")
        elif remainingDay > 0:
            return render_template('day.html', record=record, dayCount=dayCount, button="Next Day")
        else:
            session.pop('dayCount', None)
            return redirect("/list")

    if request.method == "POST":
        day_count = request.form.get("dayCount") 
        location = request.form.getlist("location")
        time = request.form.getlist("time")
        activity = request.form.getlist("activity")
        plan_id = db.session.execute(text("SELECT id FROM plan WHERE users_id = :user_id ORDER BY id DESC"), {'user_id': users_id}).fetchone()[0]
                
        # dayCount + 1 to next day.html
        session['dayCount'] = int(day_count) + 1

        # insert daily plan
        for location, time, activity in zip(location, time, activity):
            if not (location == time == activity): # skip empty row
                db.session.execute(
                    text("INSERT INTO daily_plan (plan_id, day_count, location, time, activity, created_at, updated_at) VALUES (:plan_id, :day_count, :location, :time, :activity, :created_at, :updated_at)"),
                    {"plan_id": plan_id, "day_count":day_count, "location": location , "time": time, "activity": activity, "created_at": utcnow(), "updated_at": utcnow()}
                    )
                db.session.commit()

        return redirect("/day")
```
Also, even if the user cannot finish the entire day's schedule input, they can edit it again by clicking on day x in list.html.It is because when the plan has been saved, each day will be listed in list.html.


## Database design
There are three databases: users, plan, daily_plan.
#### <img src="https://github.com/user-attachments/assets/648c1674-f05f-431b-9625-fcac6fc6a611" width="400" height="400">

About the database, "daily_plan" saves each row with time, location, and activity in day.html. 
If the user inputs ten rows of data, ten rows of data would be inserted in "daily_plan". 
When the user adds or deletes any row while editing the daily schedule, the related row data may need to be updated, deleted, or inserted.
It is difficult because there is so much information to handle. 
I chose the simpler way to solve that, so I decided to delete all old records and then insert the new data.

## Technologies Used
The website was created using Flask in Python. 
SQLite3 and SQLAlchemy are useful for setting up the database and querying it. 
Jinja passes easily the database information to HTML.
Some great interactive functions are built using JavaScript. 
CSS and Bootstrap are simple for designing a responsive and well-designed website.

## Features
1. app.py  
- list all function codes such as register, log in/out, query database, etc.
  
2. layout.html  
- display the layout  

3. plan.html  
- create new journey plan 

4. editPlan.html  
- show the related plan record
- edit journey plan with title, destination, the start date and the end date  

5. day.html  
- show the plan record
- create daily schedule 

6. editDay.html  
- show the related plan and day record
- edit daily plan with time, location, and activity  

7. list.html  
- list users' plans with time descending
- select checkbox to delete multiple plans and the related daily plans
- click the plan title link to editPlan.html 
- click the day X link to editDay.html  
- click the view icon link to view.html  

8. view.html  
- show the selected plan and daily schedule  

9. other functions with JavaScript  
- When you change the start data or the end data, the total days would be calculated automatically based on the start date and end date.  
- When you change the time point, the total time would be calculated automatically based on the two time points.  
- click the add/minus button to add/delete the row.
  
## Installation

set up the project locally

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

## Acknowledgments
- [Flask](https://flask.palletsprojects.com/en/stable/)
- [Python](https://www.python.org/)
- [SQLite3](https://www.sqlite.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Jinja](https://jinja.palletsprojects.com/en/stable/)
- [w3schools](https://www.w3schools.com/js/)
- [Bootstrap](https://getbootstrap.com/)
- [dbdiagram](https://dbdiagram.io/home)
