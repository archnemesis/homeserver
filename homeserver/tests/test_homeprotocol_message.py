import unittest
from homeserver.homeprotocol import messages


class TestMessage(unittest.TestCase):
    def test_message_header(self):
        header = messages.MessageHeader(1, 100)
        self.assertEqual(header.message_id, 1)
        self.assertEqual(header.message_size, 100)

if __name__ == "__main__":
    unittest.main()
