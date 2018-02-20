import struct
from .messages import Message


class Parser(object):
    PACKET_HEADER_MARKER = b'AE'
    PACKET_FOOTER_MARKER = b'EA'
    PACKET_HEADER_SIZE = 3

    FORMAT_HEADER = "<BH"
    FORMAT_REQUEST_CONFIG = "<"

    def __init__(self):
        self._buffer = bytearray()
        self._in_start_of_packet = False
        self._in_end_of_packet = False
        self._in_packet = False
        self._in_body = False
        self._body_bytes_remaining = 0
        self._packet_counter = 0
        self._pending_packet_header = None

        self.error_count = 0
        self.packet_count = 0

    def _reset_state(self):
        self._packet_counter = 0
        self._in_packet = False
        self._in_start_of_packet = False
        self._in_end_of_packet = False
        self._in_body = False
        self._body_bytes_remaining = 0
        self._buffer = bytearray()
        self._pending_packet_header = None

    def process_bytes(self, data):
        messages_out = []

        for b in data:
            if self._in_body:
                if self._body_bytes_remaining > 0:
                    self._buffer.append(b)
                    self._body_bytes_remaining -= 1

                if self._body_bytes_remaining == 0:
                    message_cls = Message.cls_for_message_id(self._pending_packet_header.message_id)
                    message_data = struct.unpack(message_cls.STRUCT_FORMAT, self._buffer)
                    message_obj = message_cls(*message_data)
                    messages_out.append(message_obj)

                    self._reset_state()
                    self.packet_count += 1
            else:
                if self._in_end_of_packet is True:
                    if self._packet_counter == 0:
                        if b == Parser.PACKET_FOOTER_MARKER[0]:
                            self._packet_counter = 1
                        else:
                            self._reset_state()
                            self.error_count += 1
                    elif self._packet_counter == 1:
                        if b == Parser.PACKET_FOOTER_MARKER[1]:
                            self._packet_counter = 0
                            self._in_end_of_packet = False

                            # The header packet is special message ID 0
                            packet_cls = Message.cls_for_message_id(0)
                            packet_data = struct.unpack(packet_cls.STRUCT_FORMAT, self._buffer)
                            packet_obj = packet_cls(*packet_data)

                            if packet_obj.message_size > 0:
                                self._pending_packet_header = packet_obj
                                self._body_bytes_remaining = packet_obj.message_size
                                self._in_body = True
                                self._buffer = bytearray()
                            else:
                                self.packet_count += 1
                                self._reset_state()
                        else:
                            self._reset_state()
                            self.error_count += 1
                elif self._in_packet is False:
                    if self._in_start_of_packet == False:
                        if b == Parser.PACKET_HEADER_MARKER[0]:
                            self._in_start_of_packet = True
                    else:
                        if b == Parser.PACKET_HEADER_MARKER[1]:
                            self._in_start_of_packet = False
                            self._in_packet = True
                else:
                    self._buffer.append(b)
                    self._packet_counter += 1

                    if self._packet_counter == Parser.PACKET_HEADER_SIZE:
                        self._in_packet = False
                        self._in_end_of_packet = True
                        self._packet_counter = 0
        return messages_out
