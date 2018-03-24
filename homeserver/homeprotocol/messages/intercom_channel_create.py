
import struct
from .message import Message

class IntercomChannelCreateMessage(Message):
    MESSAGE_ID = 7
    MESSAGE_SIZE = 8
    STRUCT_FORMAT = "<H6s"

    

    def __init__(self, port=0, caller=0):
        self.port = port
        self.caller = caller

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.port = data[0]
        obj.caller = data[1]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.port)
        struct_data.append(self.caller)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
