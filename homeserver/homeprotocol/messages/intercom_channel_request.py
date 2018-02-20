import struct
from .message import Message

class IntercomChannelRequestMessage(Message):
    MESSAGE_ID = 3
    MESSAGE_SIZE = 12
    STRUCT_FORMAT = "<6sIH"

    def __init__(self, hwid_caller=None, remote_channel_ip=None, remote_channel_port=None):
        self.hwid_caller = hwid_caller
        self.remote_channel_ip = remote_channel_ip
        self.remote_channel_port = remote_channel_port
    
    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.hwid_caller, self.remote_channel_ip, self.remote_channel_port)

