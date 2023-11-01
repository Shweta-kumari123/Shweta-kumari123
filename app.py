from flask import Flask, render_template, redirect, url_for, session, g, request
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_database
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_database(error):
    if hasattr(g,'hospital_db'):
        g.hospital_db.close()

def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        db = get_database()
        user_cursor = db.execute('select * from users where username = ?', [user])
        user = user_cursor.fetchone()
    return user

@app.route("/")
@app.route("/home")
def home():
    user = get_current_user()
    return render_template("home.html",  title = "Home page" , user = user)

@app.route("/login"    , methods = ["POST" , "GET"])
def login():
    user = get_current_user()
    #     1. Create a function into your main file i,e (app.py)
# 2. Check which is the method (GET or POST) 
#    GET is for fetching something from the database 
#     ex: while your loging in
#    POST is for inserting something into the database
#     ex: while registering
    if request.method == "POST":
        username = request.form['username'] 
        password = request.form['password'] #this is the user typed password in the form
# 3. Connect to the database 
        db = get_database()
        user_cursor = db.execute('select * from users where username = ?', [username] )
        user = user_cursor.fetchone()
        if user:
            if check_password_hash(user['password'], password):
                session['user'] = user['username']
                return redirect(url_for('contact'))
            else:    
                error_message = "User name or password didn't match"
                return render_template('login.html', error_message = error_message)
        else:
            error_message = "User name or password didn't match"
            return render_template('login.html', error_message = error_message)
    return render_template("login.html" , user = user)

@app.route("/register",       methods = ["POST" , "GET"])
def register():
    user = get_current_user()
    db = get_database()
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hashedpassword = generate_password_hash(password)
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        email = request.form['email']
        country = request.form['country']
        user_cursor = db.execute('select * from users where username = ?',[username])
        user = user_cursor.fetchone()
        if user:
            error_message = "User name is already exists"
            return render_template('register.html',error_message = error_message)
        db.execute('insert into users(first_name , last_name , age , email , country , username , password) values (?,?,?,?,?,?,?)' , [first_name , last_name , age , email , country , username , hashedpassword])
        db.commit()
        return redirect(url_for('login'))
    return render_template("register.html",  title = "Register page", user = user)

@app.route("/contact")
def contact():
    user = get_current_user()
    return render_template("contact.html",  title = "Contact page", user = user)

@app.route("/dashboard" ,  methods = ["POST" , "GET"])
def dashboard():
    user = get_current_user()
    db = get_database() 
    patient_cursor = db.execute("select * from appointment")
    allpatient = patient_cursor.fetchall()
    return render_template("dashboard.html" , title = "Dashboard page" , user = user , allpatient = allpatient)
@app.route("/appointment", methods=["POST", "GET"])
def appointment():
    user = get_current_user()
    db = get_database()
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        reason_for_visit = request.form['reason_for_visit']
        db.execute(
            "INSERT INTO appointment (first_name, last_name, email, phone_number, appointment_date, appointment_time, reason_for_visit) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (first_name, last_name, email, phone_number, appointment_date, appointment_time, reason_for_visit)
        )
        db.commit()
    return render_template("appointment.html", title="Appointment Page", user=user)

@app.route("/about")
def about():
    user = get_current_user()
    return render_template("about.html" ,  title = "About page" , user = user)

@app.route("/service")
def service():
    user = get_current_user()
    return render_template("service.html" ,  title = "Service page", user = user)


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for("home"))

if __name__ == "_main_":
    app.run(debug = True)