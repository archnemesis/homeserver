
import struct
from .message import Message

class IntercomDirectoryListingMessage(Message):
    MESSAGE_ID = 8
    MESSAGE_SIZE = 226
    STRUCT_FORMAT = "<HHH22s22s22s22s22s22s22s22s22s22s"

    class IntercomDirectoryListingMessageEntriesParam(object):
        STRUCT_FORMAT = "<6s16s"
        STRUCT_SIZE = 22
        
        def __init__(self, hwid=0, display_name=0):
            self.hwid = hwid
            self.display_name = display_name
        
        @classmethod
        def unpack(cls, data):
            data = struct.unpack(cls.STRUCT_FORMAT, data)
            obj = cls()
            obj.hwid = data[0]
            obj.display_name = data[1]
            
        def pack(self):
            return struct.pack(self.STRUCT_FORMAT, self.hwid, self.display_name)
    

    def __init__(self, num_entries=0, sequence=0, total=0, entries=0):
        self.num_entries = num_entries
        self.sequence = sequence
        self.total = total
        self.entries = entries

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.num_entries = data[0]
        obj.sequence = data[1]
        obj.total = data[2]
        obj.entries = []
        for i in range(10):
            obj.entries.append(cls.IntercomDirectoryListingMessageEntriesParam.unpack(data[3 + i]))
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.num_entries)
        struct_data.append(self.sequence)
        struct_data.append(self.total)
        for i in range(10):
            try:
                struct_data.append(self.entries[i].pack())
            except IndexError:
                struct_data.append(b'0' * self.IntercomDirectoryListingMessageEntriesParam.STRUCT_SIZE)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
