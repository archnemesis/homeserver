from unittest import TestCase
from unittest.mock import MagicMock
import struct

from homeserver.homeprotocol.parser import Parser


class ParserTestCase(TestCase):
    # def test_parse_message(self):
    #     test_message = struct.pack("<ccBH6sI16s", b'A', b'E', 1, 26, b'ABCDEF', 0x00AACCDD, b'thisteststring')
    #     parser = Parser()
    #     parser._on_message_received = MagicMock()
    #     messages = parser.process_bytes(test_message)
    #
    #     self.assertEqual(len(messages), 1)
    #     message = messages[0]
    #     self.assertEqual(message.hwid, b'ABCDEF')
    #     self.assertEqual(message.ipaddr, 0x00AACCDD)
    #     self.assertEqual(message.name, b'thisteststring\x00\x00')
    #
    # def test_parse_message_error_count(self):
    #     test_message = b'AE420u9fdsafdsagsafdsa;'
    #     parser = Parser()
    #     messages = parser.process_bytes(test_message)
    #
    #     self.assertEqual(len(messages), 0)
    #     self.assertEqual(parser.error_count, 1)

    def test_parse_message(self):
        parser = Parser()
        messages = parser.process_bytes(b'AE\x01\x1a\x00\x00\x01\x02\x03\x04\x05\n\x01\x01\x8ctest\x00\x00')
        self.assertEqual(len(messages), 1)
