

class HomeProtocol(object):
    START_OF_PACKET = b"EA"

    def __init__(self):
        self.buffer = bytes()
        self._start_of_packet = False
        self._in_packet = False
        self._in_body = False
        self._pending_packet_type = None

    def process_bytes(self, data):
        for b in data:
            if self._in_packet is False:
                if self._start_of_packet == False:
                    if b == START_OF_PACKET[0]:
                        self._start_of_packet = True
                else:
                    if b == START_OF_PACKET[1]:
                        self._start_of_packet = False
                        self._in_packet = True
            else:
                if not self._in_body:
