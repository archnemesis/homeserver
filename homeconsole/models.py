from flask_mongoengine import MongoEngine
from flask_mongoengine.wtf import model_form

db = MongoEngine()


class Profile(db.Document):
    name = db.StringField(required=True, max_length=32)
    description = db.StringField()


class DeviceEndpoint(db.EmbeddedDocument):
    ENDPOINT_TYPE_CONTROL = "control"
    ENDPOINT_TYPE_SENSOR = "sensor"
    ENDPOINT_TYPE_CHOICES = [
        (ENDPOINT_TYPE_CONTROL, "Control"),
        (ENDPOINT_TYPE_SENSOR, "Sensor")
    ]

    SENSOR_TYPE_NONE = ""
    SENSOR_TYPE_TEMPERATURE = "temperature"
    SENSOR_TYPE_LIGHT = "light"
    SENSOR_TYPE_HUMIDITY = "humidity"
    SENSOR_TYPE_WIND_SPEED = "wind_speed"
    SENSOR_TYPE_WIND_DIRECTION = "wind_direction"
    SENSOR_TYPE_DOOR = "door"
    SENSOR_TYPE_WINDOW = "window"
    SENSOR_TYPE_CAMERA = "camera"
    SENSOR_TYPE_MOTION = "motion"
    SENSOR_TYPE_FIRE = "fire"
    SENSOR_TYPE_CHOICES = [
        (SENSOR_TYPE_NONE, ""),
        (SENSOR_TYPE_TEMPERATURE, "Temperature"),
        (SENSOR_TYPE_LIGHT, "Light"),
        (SENSOR_TYPE_HUMIDITY, "Humidity"),
        (SENSOR_TYPE_WIND_SPEED, "Windspeed"),
        (SENSOR_TYPE_WIND_DIRECTION, "Wind Direction"),
        (SENSOR_TYPE_DOOR, "Door"),
        (SENSOR_TYPE_WINDOW, "Window"),
        (SENSOR_TYPE_CAMERA, "Camera"),
        (SENSOR_TYPE_MOTION, "Motion"),
        (SENSOR_TYPE_FIRE, "Fire"),
    ]

    CONTROL_TYPE_NONE = ""
    CONTROL_TYPE_SWITCH = "switch"
    CONTROL_TYPE_DIMMER = "dimmer"
    CONTROL_TYPE_DOOR = "door"
    CONTROL_TYPE_HVAC = "hvac"
    CONTROL_TYPE_CHOICES = [
        (CONTROL_TYPE_NONE, ""),
        (CONTROL_TYPE_SWITCH, "Switch"),
        (CONTROL_TYPE_DIMMER, "Dimmer"),
        (CONTROL_TYPE_DOOR, "Door"),
        (CONTROL_TYPE_HVAC, "HVAC"),
    ]

    endpoint_id = db.IntField(required=True)
    endpoint_type = db.StringField(choices=ENDPOINT_TYPE_CHOICES)
    sensor_type = db.StringField(choices=SENSOR_TYPE_CHOICES, default=SENSOR_TYPE_NONE)
    control_type = db.StringField(choices=CONTROL_TYPE_CHOICES, default=CONTROL_TYPE_NONE)
    name = db.StringField(max_length=32)
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
    endpoints = db.ListField(db.EmbeddedDocumentField(DeviceEndpoint))

DeviceForm = model_form(Device, exclude=["created", "updated"], field_args={
    "endpoints": {
        "min_entries": 0
    }
})
