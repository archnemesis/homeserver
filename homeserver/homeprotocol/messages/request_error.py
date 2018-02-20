import struct
from .message import Message

class RequestErrorMessage(Message):
    MESSAGE_ID = 2
    MESSAGE_SIZE = 20
    STRUCT_FORMAT = "<I16s"

    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message
    
    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.code, self.message)

