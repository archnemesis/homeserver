
import struct
from .message import Message

class IntercomChannelAcceptMessage(Message):
    MESSAGE_ID = 4
    MESSAGE_SIZE = 6
    STRUCT_FORMAT = "<IH"

    

    def __init__(self, remote_addr=0, remote_port=0):
        self.remote_addr = remote_addr
        self.remote_port = remote_port

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.remote_addr = data[0]
        obj.remote_port = data[1]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.remote_addr)
        struct_data.append(self.remote_port)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
