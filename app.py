import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# std timezone
def utcnow():
    return datetime.now(timezone.utc)

# set database
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String, nullable=False, unique=False)
    hash = db.Column(db.String, nullable=False)
    plans = db.relationship('Plan', backref='user', lazy=True)

class Plan(db.Model):
    __tablename__ = 'plan'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_day = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    daily_plans = db.relationship('DailyPlan', backref='plan', lazy=True)

class DailyPlan(db.Model):
    __tablename__ = 'daily_plan'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    day_count = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String, nullable=False)
    time = db.Column(db.Time, nullable=False)
    activity = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, nullable=False)

with app.app_context():
    db.create_all()

    # check table content
    tables = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    print("Tables in the database:", tables)
    
    # check plan content
    plan = db.session.execute(text("SELECT * FROM plan")).fetchall()
    print(plan)

    # reset table
    # db.drop_all()
    db.session.commit()  


if __name__ == "__main__":
    app.run(debug=True)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request 
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def layout():
    return render_template('layout.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        plaintext_password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not plaintext_password or not confirmation:
            flash("Missing input")
            return render_template("register.html")

        if plaintext_password != confirmation:
            flash("Password not match")
            return render_template("register.html")

        user = db.session.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username}).fetchone()

        if not user:
            password = generate_password_hash(plaintext_password, method='scrypt', salt_length=16)
            db.session.execute(text("INSERT INTO users (username, hash) VALUES (:username, :hash)"), {"username": username, "hash": password})
            db.session.commit()
            flash("Registration successful!")
            return render_template("login.html")
        else:
            flash("The username already exists.")
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            flash("Missing input")
            return render_template("login.html")

        user = User.query.filter_by(username=request.form.get("username")).first()

        if not user or not check_password_hash(user.hash, request.form.get("password")):
            flash("Invalid input")
            return render_template("login.html")

        session["user_id"] = user.id
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/plan", methods=["GET", "POST"])
def plan():
    if request.method == "POST":
        title = request.form.get("title")
        destination = request.form.get("destination")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        total_day = request.form.get("total_day")
        users_id = session["user_id"]

        if not title or not destination or not start_date or not end_date or not total_day or total_day == "0":
            flash("Missing input")
            return redirect("/plan")

        # insert new plan into the database
        db.session.execute(
            text("INSERT INTO plan (users_id, title, destination, start_date, end_date, total_day, created_at, updated_at) VALUES (:users_id, :title, :destination, :start_date, :end_date, :total_day, :created_at, :updated_at)"),
            {
                "users_id": users_id,
                "title": title,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "total_day": total_day,
                "created_at": utcnow(),
                "updated_at": utcnow()
            }
        )
        db.session.commit() 
        
        return redirect("/day")
    
    return render_template('plan.html')

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

@app.route("/list", methods=["GET", "POST"])
def list():
    # show all plan
    if request.method == "GET":
        users_id = session["user_id"]
        plan_records = db.session.execute(text("SELECT * FROM plan WHERE users_id = :users_id ORDER BY created_at DESC"),{'users_id': users_id}).fetchall()

        if not plan_records:
            return render_template('list.html', notPlan = "Go to plan your journey" )
        
        return render_template('list.html', plan_records=plan_records)
    
    # delete all selected plan
    if request.method == "POST":
        plan_id = request.form.getlist("plan_id")

        for id in plan_id:
            db.session.execute(
                text("DELETE FROM plan WHERE id = :id"),
                {"id": id}
            )
        db.session.commit()
        
        return redirect('/list')

@app.route("/editDay", methods=["GET", "POST"])
def editDay():
    if request.method == "GET":
        users_id = session["user_id"]
        plan_id = request.args.get('plan')
        day_count = request.args.get('day')

        #the user's plan
        plan_records = db.session.execute(
            text("SELECT * FROM plan WHERE id = :plan_id AND users_id = :users_id"),
            {'plan_id': plan_id, 'users_id': users_id}
        ).fetchone()        
        
        # the user's daily_plan
        daily_records = db.session.execute(
            text("SELECT * FROM daily_plan WHERE day_count = :day_count AND plan_id = :plan_id ORDER BY time ASC"),
            {'plan_id': plan_id, 'day_count': day_count}
        ).fetchall() 

        return render_template('editDay.html', record=plan_records, daily_records=daily_records, day_count=day_count)
    
    if request.method == "POST":
        day_count = request.form.get("dayCount") 
        location = request.form.getlist("location")
        time = request.form.getlist("time")
        activity = request.form.getlist("activity")
        plan_id = request.form.get("plan_id") 
        
        # delete old data
        db.session.execute(
            text("DELETE FROM daily_plan WHERE plan_id = :plan_id AND day_count = :day_count"),
            {"plan_id": plan_id, 'day_count': day_count}
        )
        db.session.commit()
        
        # insert new data
        for location, time, activity in zip(location, time, activity):            
            if not (location == time == activity): # skip empty row
                update = db.session.execute(
                    text("INSERT INTO daily_plan (plan_id, day_count, location, time, activity, created_at, updated_at) VALUES (:plan_id, :day_count, :location, :time, :activity, :created_at, :updated_at)"),
                    {"plan_id": plan_id, "day_count":day_count, "location": location , "time": time, "activity": activity, "created_at": utcnow(), "updated_at": utcnow()}
                    )

            db.session.commit()
        return redirect('/list')

@app.route("/editPlan", methods=["GET", "POST"])
def editPlan():
    if request.method == "GET":
        users_id = session["user_id"]
        plan_id = request.args.get('plan')

        record = db.session.execute(
            text("SELECT * FROM plan WHERE id = :plan_id AND users_id = :users_id"),
            {'plan_id': plan_id, 'users_id': users_id}
        ).fetchone()
        
        return render_template("editPlan.html", record=record)
    
    if request.method == "POST":
        title = request.form.get("title")
        destination = request.form.get("destination")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        total_day = request.form.get("total_day")
        users_id = session["user_id"]
        plan_id = request.form.get("plan_id")
        total_day = request.form.get("total_day") 

        if not title or not destination or not start_date or not end_date or not total_day:
            flash("Input Missing")
            return redirect("/list")

        plan = db.session.execute(
            text("SELECT * FROM plan WHERE id = :plan_id AND users_id = :users_id"),
            {'plan_id': plan_id, 'users_id': users_id}
        ).fetchone()

        # update plan
        if plan.total_day == int(total_day):
            db.session.execute(
            text("""
                UPDATE plan 
                SET title = :title, destination = :destination, start_date = :start_date, end_date = :end_date, updated_at =:updated_at
                WHERE id = :plan_id 
            """),
            {
                "title": title,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "plan_id" : plan_id,
                "updated_at": utcnow()
            }
            )
            db.session.commit()
        else:
            flash("Can not change total day")
    
    return redirect("/list")

@app.route("/view", methods=["GET", "POST"])
def view():
    if request.method == "GET":
        plan_id = request.args.get("plan")

        plan_records = db.session.execute(
                text("SELECT * FROM plan WHERE id = :plan_id"),
                {'plan_id': plan_id}
            ).fetchone()
        
        daily_records = db.session.execute(
            text("SELECT * FROM daily_plan WHERE plan_id = :plan_id ORDER BY time ASC"),
            {'plan_id': plan_id}
        ).fetchall() 
        
        return render_template('view.html', record=plan_records, daily_records=daily_records)