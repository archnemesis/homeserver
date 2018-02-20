import unittest
from homeserver.homeprotocol import messages


class TestMessage(unittest.TestCase):
    def test_message_header(self):
        header = messages.MessageHeader(1, 100)
        self.assertEqual(header.message_id, 1)
        self.assertEqual(header.message_size, 100)

    def test_request_configuration_message(self):
        message = messages.RequestConfigurationMessage()
        message.hwid = b'ABCDEF'
        message.ipaddr = 0xAABBCCDD
        message.name = b'test'
        message_bytes = message.pack()

        self.assertEqual(message_bytes, b'ABCDEF\xdd\xcc\xbb\xaatest\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

if __name__ == "__main__":
    unittest.main()
