
import struct
from .message import Message

class IntercomIncomingChannelRequestMessage(Message):
    MESSAGE_ID = 9
    MESSAGE_SIZE = 38
    STRUCT_FORMAT = "<6s16s16s"

    

    def __init__(self, caller_hwid=0, display_name=0, description=0):
        self.caller_hwid = caller_hwid
        self.display_name = display_name
        self.description = description

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.caller_hwid = data[0]
        obj.display_name = data[1]
        obj.description = data[2]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.caller_hwid)
        struct_data.append(self.display_name)
        struct_data.append(self.description)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
