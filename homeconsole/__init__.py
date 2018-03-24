import datetime
from bson import ObjectId

from flask import Flask
from flask import render_template, request, flash, redirect, url_for
from flask_pymongo import PyMongo

from .forms import UserCreateForm
from .forms import DeviceCreateForm
from .models import db as model_db, Device, DeviceForm

app = Flask(__name__)
app.config.from_envvar("HOMECONSOLE_SETTINGS")
mongo = PyMongo(app)
model_db.init_app(app)

@app.route('/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/devices')
def device_list():
    devices = Device.objects()
    return render_template('device_list.html', devices=devices)

@app.route('/devices/create')
def device_create():
    if request.method == 'POST':
        mongo.db.devices.insert_one({
            "hwid": request.form['hwid'],
            "name": request.form['name'],
            "description": request.form['description'],
            "device_type": request.form['device_type'],
            "active": request.form['active'],
            "created": datetime.datetime.utcnow(),
            "updated": None
        })
        flash("Device {} was created successfully.".format(request.form['name']), 'info')
        return redirect(url_for('device_list'))
    else:
        form = DeviceForm()
        return render_template("device_form.html", form=form)

@app.route('/devices/<string:device_id>/configure', methods=['GET', 'POST'])
def device_configure(device_id):
    try:
        device = Device.objects.get(pk=ObjectId(device_id))
    except Device.DoesNotExist:
        flash("Device {} does not exist.".format(device_id), 'warning')
        return redirect(url_for('device_list'))

    if request.method == 'POST':
        form = DeviceForm(request.form, instance=device)
        if form.validate():
            form.save(commit=False)
            device.updated = datetime.datetime.utcnow()
            device.save()
            flash("Device updated successfully.", 'info')
            return redirect(url_for('device_list'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash("Error in field %s: %s" % (getattr(form, field).label.text, error), 'error')
    else:
        form = DeviceForm(instance=device)

    return render_template("device_form.html", device=device, form=form)

@app.route('/devices/<string:device_id>/remove')
def device_remove(device_id):
    try:
        device = Device.objects.get(pk=ObjectId(device_id))
    except Device.DoesNotExist:
        flash("Device {} does not exist.".format(device_id), 'warning')
        return redirect(url_for('device_list'))
    device.delete()
    flash("Device {} was removed.".format(device.name), 'info')
    return redirect(url_for('device_list'))

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
