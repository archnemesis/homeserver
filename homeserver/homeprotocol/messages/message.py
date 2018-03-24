
import struct


MESSAGE_HEADER_SIZE = 13
MESSAGE_MAX_DATA_SIZE = 234
MESSAGE_MAX_TOTAL_SIZE = MESSAGE_HEADER_SIZE + MESSAGE_MAX_DATA_SIZE


def pack_message(message):
    header = MessageHeader()
    header.message_id = message.MESSAGE_ID
    header.message_size = message.MESSAGE_SIZE
    header_data = header.pack()
    message_data = message.pack()

    data = struct.pack('<cc%ds%ds' % (header.MESSAGE_SIZE, message.MESSAGE_SIZE), b'A', b'E', header_data, message_data)
    return data


class ErrorCode(object):
    RequestError = 1
    RequestDeniedPermissions = 2
    RequestDeniedUnRegistered = 3
    RequestFailed = 4
class DeviceType(object):
    Computer = 1
    WallPanelSmall = 2
    WallPanelMedium = 3
    WallPanelLarge = 4
    Keypad = 5
class DeviceUITheme(object):
    Default = 1
    Light = 2
    Dark = 3
class ControlType(object):
    OnOff = 1
    Slider = 2
    Momentary = 3


class Message(object):
    @classmethod
    def cls_for_message_id(cls, message_id):
        for subclass in cls.__subclasses__():
            if subclass.MESSAGE_ID == message_id:
                return subclass
        else:
            raise RuntimeError("No message class matching %s" % message_id)


class MessageHeader(Message):
    MESSAGE_ID = 0
    MESSAGE_SIZE = 13
    STRUCT_FORMAT = "<BH6sI"

    def __init__(self, message_id=None, message_size=None, hwid=None, timestamp=None):
        self.message_id = message_id
        self.message_size = message_size
        self.hwid = hwid
        self.timestamp = timestamp

    def __str__(self):
        return "<MessageHeader(%d, %d)>" % (self.message_id, self.message_size)

    @classmethod
    def unpack(cls, data):
        msg_data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.message_id = msg_data[0]
        obj.message_size = msg_data[1]
        obj.hwid = msg_data[2]
        obj.timestamp = msg_data[3]
        return obj

    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.message_id, self.message_size, self.hwid, self.timestamp)
