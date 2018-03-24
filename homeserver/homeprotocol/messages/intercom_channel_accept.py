
import struct
from .message import Message

class IntercomChannelAcceptMessage(Message):
    MESSAGE_ID = 4
    MESSAGE_SIZE = 8
    STRUCT_FORMAT = "<6sH"

    

    def __init__(self, hwid_callee=0, remote_port=0):
        self.hwid_callee = hwid_callee
        self.remote_port = remote_port

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.hwid_callee = data[0]
        obj.remote_port = data[1]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.hwid_callee)
        struct_data.append(self.remote_port)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
