
import struct
from .message import Message

class ConfigurationPayloadMessage(Message):
    MESSAGE_ID = 5
    MESSAGE_SIZE = 234
    STRUCT_FORMAT = "<32s32sH42s42s42s42s"

    class ConfigurationPayloadMessageControlsParam(object):
        STRUCT_FORMAT = "<HII16s16s"
        STRUCT_SIZE = 42
        
        def __init__(self, controltype=0, min=0, max=0, name=0, description=0):
            self.controltype = controltype
            self.min = min
            self.max = max
            self.name = name
            self.description = description
        
        @classmethod
        def unpack(cls, data):
            data = struct.unpack(cls.STRUCT_FORMAT, data)
            obj = cls()
            obj.controltype = data[0]
            obj.min = data[1]
            obj.max = data[2]
            obj.name = data[3]
            obj.description = data[4]
            
        def pack(self):
            return struct.pack(self.STRUCT_FORMAT, self.controltype, self.min, self.max, self.name, self.description)
    

    def __init__(self, display_name=0, description=0, theme=0, controls=0):
        self.display_name = display_name
        self.description = description
        self.theme = theme
        self.controls = controls

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.display_name = data[0]
        obj.description = data[1]
        obj.theme = data[2]
        obj.controls = []
        for i in range(4):
            obj.controls.append(cls.ConfigurationPayloadMessageControlsParam.unpack(data[3 + i]))
        return obj

    def pack(self):
        struct_data = []
        struct_data.append(self.display_name)
        struct_data.append(self.description)
        struct_data.append(self.theme)
        for i in range(4):
            try:
                struct_data.append(self.controls[i].pack())
            except IndexError:
                struct_data.append(b'0' * self.ConfigurationPayloadMessageControlsParam.STRUCT_SIZE)
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
