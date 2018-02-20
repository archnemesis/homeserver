import struct
from .message import Message

class ConfigurationPayloadMessage(Message):
    MESSAGE_ID = 5
    MESSAGE_SIZE = 66
    STRUCT_FORMAT = "<32s32sH"

    def __init__(self, display_name=None, description=None, theme=None):
        self.display_name = display_name
        self.description = description
        self.theme = theme
    
    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.display_name, self.description, self.theme)

