from flask_mongoengine import MongoEngine
from flask_mongoengine.wtf import model_form

db = MongoEngine()


class Profile(db.Document):
    name = db.StringField(required=True, max_length=32)
    description = db.StringField()



class Device(db.Document):
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

    hwid = db.StringField(required=True, max_length=20)
    name = db.StringField(required=True, max_length=16)
    description = db.StringField(max_length=32)
    device_type = db.IntField(required=True, choices=DEVICE_TYPE_CHOICES)
    active = db.BooleanField()
    created = db.DateTimeField(required=True)
    updated = db.DateTimeField(required=True)

DeviceForm = model_form(Device, exclude=["created", "updated"])
