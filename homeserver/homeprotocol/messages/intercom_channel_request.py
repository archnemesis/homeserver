
import struct
from .message import Message

class IntercomChannelRequestMessage(Message):
    MESSAGE_ID = 3
    MESSAGE_SIZE = 6
    STRUCT_FORMAT = "<6s"

    

    def __init__(self, hwid_callee=0):
        self.hwid_callee = hwid_callee

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.hwid_callee = data[0]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.hwid_callee)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
