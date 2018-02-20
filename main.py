import argparse
import socketserver
import ipaddress
from homeserver.homeprotocol import messages
from homeserver.homeprotocol.parser import Parser


class HomeServerTCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        self.parser = Parser()
        super().__init__(*args, **kwargs)

    def handle(self):
        self.request.settimeout(1)

        while True:
            try:
                data = self.request.recv(1024)
            except socket.timeout as e:
                pass
            except socket.error as e:
                return
            else:
                if len(data) == 0:
                    print("Connection closed")
                    return

                for message in self.parser.process_bytes(data):
                    if type(message) is messages.RequestConfigurationMessage:
                        pass

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
