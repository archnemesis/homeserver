from flask_wtf import FlaskForm
from wtforms import fields
from wtforms.validators import DataRequired


class UserCreateForm(FlaskForm):
    username = fields.StringField("Username")
    password = fields.PasswordField("Password")
    email = fields.StringField("Email Address")
    first_name = fields.StringField("First Name")
    last_name = fields.StringField("Last Name")


class DeviceCreateForm(FlaskForm):
    DEVICE_TYPE_PANEL_SMALL = 1
    DEVICE_TYPE_PANEL_MEDIUM = 2
    DEVICE_TYPE_PANEL_LARGE = 3
    DEVICE_TYPE_DESKTOP = 4
    DEVICE_TYPE_CHOICES = [
        (DEVICE_TYPE_PANEL_SMALL, "Small Panel"),
        (DEVICE_TYPE_PANEL_MEDIUM, "Medium Panel"),
        (DEVICE_TYPE_PANEL_LARGE, "Large Panel"),
        (DEVICE_TYPE_DESKTOP, "Desktop")
    ]

    name = fields.StringField("Name")
    description = fields.StringField("Description")
    hwid = fields.StringField("Hardware ID")
    device_type = fields.SelectField("Device Type", choices=DEVICE_TYPE_CHOICES)
    active = fields.BooleanField("Active")
    
