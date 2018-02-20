import struct
from .message import Message

class IntercomIncomingChannelAcceptMessage(Message):
    MESSAGE_ID = 3
    MESSAGE_SIZE = 12
    STRUCT_FORMAT = "<6sIH"

    def __init__(self, hwid_caller=None, local_channel_ip=None, local_channel_port=None):
        self.hwid_caller = hwid_caller
        self.local_channel_ip = local_channel_ip
        self.local_channel_port = local_channel_port
    
    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.hwid_caller, self.local_channel_ip, self.local_channel_port)

