
import struct
from .message import Message

class RequestErrorMessage(Message):
    MESSAGE_ID = 2
    MESSAGE_SIZE = 18
    STRUCT_FORMAT = "<H16s"

    

    def __init__(self, code=0, message=0):
        self.code = code
        self.message = message

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.code = data[0]
        obj.message = data[1]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.code)
        struct_data.append(self.message)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
