import struct
from .message import Message

class RequestErrorMessage(Message):
    MESSAGE_ID = 2
    MESSAGE_SIZE = 18
    STRUCT_FORMAT = "<H16s"

    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message
    
    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.code, self.message)

