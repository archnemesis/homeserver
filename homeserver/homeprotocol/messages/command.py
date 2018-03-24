
import struct
from .message import Message

class CommandMessage(Message):
    MESSAGE_ID = 1
    MESSAGE_SIZE = 2
    STRUCT_FORMAT = "<H"

    

    def __init__(self, command_id=0):
        self.command_id = command_id

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.command_id = data[0]
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.command_id)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
