
import struct
from .message import Message

class IntercomIncomingChannelRequestMessage(Message):
    MESSAGE_ID = 9
    MESSAGE_SIZE = 42
    STRUCT_FORMAT = "<6sI16s16s"

    

    def __init__(self, caller_hwid=0, addr=0, display_name=0, description=0):
        self.caller_hwid = caller_hwid
        self.addr = addr
        self.display_name = display_name
        self.description = description

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.caller_hwid = data[0]
        obj.addr = data[1]
        obj.display_name = data[2]
        obj.description = data[3]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.caller_hwid)
        struct_data.append(self.addr)
        struct_data.append(self.display_name)
        struct_data.append(self.description)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
