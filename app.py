# Imports

import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

# 'MONGO_URI' and 'EMAILJS_KEY' stored in Enviroment Variables


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# Function to load 'Home' page as default


@app.route('/')
def home():
    countries = mongo.db.countries.find()
    return render_template("index.html",
                           countries=countries)

# Function to load 'Register' page


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if email already exists in db
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "name": request.form.get("name"),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("email")
        flash("Registration Successful!")
        return redirect(url_for("profile", email=session["user"]))

    return render_template("register.html")

# Function to load 'login' page


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if email exists in db
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email")})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("email").lower()
                flash("Welcome, {}".format(
                    request.form.get("email")))
                return redirect(url_for(
                    "profile", email=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # email doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


# Function to load 'logout' page

@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Function to load 'Profile' page

@app.route("/profile/<email>", methods=["GET", "POST"])
def profile(email):
    # grab the session user's email from db
    email = mongo.db.users.find_one(
        {"email": session["user"]})["email"]
    # grab the session user's name from db
    name = mongo.db.users.find_one(
        {"email": session["user"]})["name"]

    if session["user"]:
        return render_template("profile.html", email=email, name=name)

    return redirect(url_for("login"))


# Function to load 'Catches' page

@app.route("/get_catches")
def get_catches():
    catches = list(mongo.db.catches.find())
    return render_template("magnet_catch_log/catches.html", catches=catches)


@app.route("/add_catch", methods=["GET", "POST"])
def add_catch():
    if request.method == "POST":
        catch = {
            "date": request.form.get("date"),
            "country": request.form.get("country"),
            "city": request.form.get("city"),
            "created_by": session["user"]
        }
        mongo.db.catches.insert_one(catch)
        flash("Catch Successfully Added")
        return redirect(url_for("get_catches"))

    return render_template("magnet_catch_log/add_catch.html")


@app.route("/edit_catch/<catch_id>", methods=["GET", "POST"])
def edit_catch(catch_id):
    if request.method == "POST":
        submit = {
            "date": request.form.get("date"),
            "country": request.form.get("country"),
            "city": request.form.get("city"),
            "created_by": session["user"]
        }
        mongo.db.catches.update({"_id": ObjectId(catch_id)}, submit)
        flash("Task Successfully Updated")
        return redirect(url_for("get_catches"))

    catch = mongo.db.catches.find_one({"_id": ObjectId(catch_id)})
    return render_template("magnet_catch_log/edit_catch.html", catch=catch)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
