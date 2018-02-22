
import struct
from .message import Message

class IntercomChannelAcceptMessage(Message):
    MESSAGE_ID = 4
    MESSAGE_SIZE = 12
    STRUCT_FORMAT = "<6sIH"

    

    def __init__(self, hwid_caller=None, local_channel_ip=None, local_channel_port=None):
        self.hwid_caller = hwid_caller
        self.local_channel_ip = local_channel_ip
        self.local_channel_port = local_channel_port

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.hwid_caller = data[0]
        obj.local_channel_ip = data[1]
        obj.local_channel_port = data[2]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.hwid_caller)
        struct_data.append(self.local_channel_ip)
        struct_data.append(self.local_channel_port)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
