
import struct
from .message import Message

class IntercomChannelRequestMessage(Message):
    MESSAGE_ID = 3
    MESSAGE_SIZE = 12
    STRUCT_FORMAT = "<6s6s"

    

    def __init__(self, hwid_caller=None, hwid_callee=None):
        self.hwid_caller = hwid_caller
        self.hwid_callee = hwid_callee

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.hwid_caller = data[0]
        obj.hwid_callee = data[1]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.hwid_caller)
        struct_data.append(self.hwid_callee)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
