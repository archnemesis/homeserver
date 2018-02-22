import datetime

from flask import Flask
from flask import render_template, request, flash, redirect
from flask_pymongo import PyMongo

from .forms import UserCreateForm

app = Flask(__name__)
app.config.from_envvar("HOMECONSOLE_SETTINGS")
mongo = PyMongo(app)

@app.route('/')
def hello_world():
    return render_template("dashboard.html")

@app.route('/devices')
def device_list():
    devices = mongo.db.devices.find()
    return render_template('device_list.html', devices=devices)

@app.route('/devices/create')
def device_create():
    if request.method == 'POST':
        mongo.db.devices.insert_one({
            "hwid": request.form['hwid'],
            "name": request.form['name'],
            "description": request.form['description'],
            "device_type": request.form['device_type'],
            "registered": True,
            "created": datetime.datetime.utcnow(),
            "updated": None
        })

@app.route('/users')
def user_list():
    users = mongo.db.users.find()
    return render_template('user_list.html', users=users)

@app.route('/users/create')
def user_create():
    if request.method == "POST":
        mongo.db.users.insert_one({
            "username": request.form['username'],
            "password": request.form['password'],
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "email": request.form['email'],
            "created": datetime.datetime.utcnow(),
            "updated": None
        })
        flash("User \"{}\" was created successfully.".format(request.form['username']))
        return redirect(url_for('user_list'))
    else:
        form = UserCreateForm()
        return render_template("user_create.html", form=form)
