import argparse
import socketserver
import socket
import ipaddress
from homeserver.homeprotocol import messages
from homeserver.homeprotocol.parser import Parser


class HomeServerTCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        self.parser = Parser()
        super().__init__(*args, **kwargs)

    def handle(self):
        self.request.settimeout(1)
        timeout_counter = 0

        while True:
            try:
                data = self.request.recv(1024)
            except socket.timeout as e:
                timeout_counter += 1
                if timeout_counter > 30:
                    print("Connection closed")
                    return
            except socket.error as e:
                return
            else:
                if len(data) == 0:
                    print("Connection closed")
                    return
                print("Got data: %r" % data)
                for message in self.parser.process_bytes(data):
                    if type(message) is messages.RequestConfigurationMessage:
                        payload = messages.ConfigurationPayloadMessage()
                        payload.display_name = b'Test Device'
                        payload.description = b'Test Device 1 STM32'
                        payload.theme = messages.DeviceUITheme.Default
                        msg_bytes = messages.pack_message(payload)
                        self.request.sendall(msg_bytes)

        print("End connection")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("address", help="Address to listen for connections on")
    parser.add_argument("port", type=int, default=2005, help="Service port number")
    args = parser.parse_args()

    address = args.address
    port = args.port

    print("Starting server on %s:%d..." % (address, port))
    server = socketserver.TCPServer((address, port), HomeServerTCPHandler)
    server.serve_forever()
