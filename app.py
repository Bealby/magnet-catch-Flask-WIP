# Imports

import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

# 'MONGO_URI' and 'EMAILJS_KEY' stored in Enviroment Variables

app.config["MONGO_DBNAME"] = 'magnet_fishing'
app.config["MONGO_URI"] = os.getenv('MONGO_URI')

EMAILJS_KEY = os.environ.get("EMAILJS_KEY")

mongo = PyMongo(app)

# Function to load 'Home' page as default


@app.route('/')
def home():
    return render_template("intro-communication/index.html")

# Function to load 'Contact' page


@app.route('/contact')
def contact():
    return render_template("intro-communication/contact.html",
                           EMAILJS_KEY=EMAILJS_KEY)

# Function to load 'Catch' data from MongoDB, to render in Catch
# Log respectively


@app.route('/catch_log')
@app.route('/get_catches')
def get_catches():
    return render_template("catches/catch_log.html",
                           catch_log=mongo.db.catch_log.find())


# Function to 'Add_Catches' in database

@app.route('/add_catches')
def add_catches():
    return render_template('catches/add_catches.html',
                           area=mongo.db.area.find(),
                           magnet=mongo.db.magnet.find())

# Function to 'Insert Catches' in database


@app.route('/insert_catches', methods=['POST'])
def insert_catches():
    catch_log = mongo.db.catch_log
    catch_log.insert_one(request.form.to_dict())
    return redirect(url_for('get_catches'))

# Function to 'Add_Catches' in database


@app.route('/edit_catch_log/<catch_log_id>')
def edit_catch_log(catch_log_id):
    the_catch_log = mongo.db.catch_log.find_one({"_id":
                                                ObjectId(catch_log_id)})
    all_area = mongo.db.area.find()
    all_magnet = mongo.db.magnet.find()
    return render_template('catches/edit_catch_log.html',
                           catch_log=the_catch_log,
                           area=all_area, magnet=all_magnet)

# Function to 'Update Catches' in database


@app.route('/update_catch_log/<catch_log_id>', methods=["POST"])
def update_catch_log(catch_log_id):
    catch_log = mongo.db.catch_log
    catch_log.update({'_id': ObjectId(catch_log_id)},
                     {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'magnet': request.form.get('magnet'),
        'area_name': request.form.get('area_name'),
        'location_name': request.form.get('location_name'),
        'catch_1': request.form.get('catch_1'),
        'catch_2': request.form.get('catch_2'),
        'catch_3': request.form.get('catch_3'),
        'catch_4': request.form.get('catch_4'),
        'catch_5': request.form.get('catch_5'),
        'catch_date': request.form.get('catch_date')
    })
    return redirect(url_for('get_catches'))

# Function to 'Delete Catches' in database


@app.route('/delete_catch_log/<catch_log_id>')
def delete_catch_log(catch_log_id):
    mongo.db.catch_log.remove({'_id': ObjectId(catch_log_id)})
    return redirect(url_for('get_catches'))

# Functions to handle 404 & 500 errors


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error-messages/404.html'), 404


@app.errorhandler(500)
def something_wrong(error):
    return render_template('error-messages/500.html'), 500

# IP and PORT


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)
