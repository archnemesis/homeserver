
import struct
from .message import Message

class RequestConfigurationMessage(Message):
    MESSAGE_ID = 1
    MESSAGE_SIZE = 26
    STRUCT_FORMAT = "<6sI16s"

    

    def __init__(self, hwid=None, ipaddr=None, name=None):
        self.hwid = hwid
        self.ipaddr = ipaddr
        self.name = name

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.hwid = data[0]
        obj.ipaddr = data[1]
        obj.name = data[2]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.hwid)
        struct_data.append(self.ipaddr)
        struct_data.append(self.name)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
