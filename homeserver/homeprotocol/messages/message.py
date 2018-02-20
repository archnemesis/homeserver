
import struct


def pack_message(message):
    header = MessageHeader()
    header.message_id = message.MESSAGE_ID
    header.message_size = message.MESSAGE_SIZE
    header_data = header.pack()
    message_data = message.pack()

    data = struct.pack('<cc3s%ds' % message.MESSAGE_SIZE, b'A', b'E', header_data, message_data)
    return data


class ErrorCodes(object):
    RequestError = 0
    RequestDeniedPermissions = 1
    RequestDeniedUnRegistered = 2
    RequestFailed = 3


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
    MESSAGE_SIZE = 3
    STRUCT_FORMAT = "<BH"

    def __init__(self, message_id=None, message_size=None):
        self.message_id = message_id
        self.message_size = message_size

    def __str__(self):
        return "<MessageHeader(%d, %d)>" % (self.message_id, self.message_size)

    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.message_id, self.message_size)
