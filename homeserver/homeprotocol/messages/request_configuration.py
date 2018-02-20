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
    
    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.hwid, self.ipaddr, self.name)

