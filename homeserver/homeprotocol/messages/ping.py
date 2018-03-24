
import struct
from .message import Message

class PingMessage(Message):
    MESSAGE_ID = 6
    MESSAGE_SIZE = 4
    STRUCT_FORMAT = "<I"

    

    def __init__(self, timestamp=0):
        self.timestamp = timestamp

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.timestamp = data[0]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.timestamp)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
