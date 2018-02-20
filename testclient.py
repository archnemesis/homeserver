import socket
import ipaddress
import sys
import argparse

from homeserver.homeprotocol.messages import pack_message
from homeserver.homeprotocol.messages import RequestConfigurationMessage

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Hostname or IP address of HomeServer")
    parser.add_argument("port", type=int, help="Service port number")
    args = parser.parse_args()

    host = args.host
    port = args.port

    msg = RequestConfigurationMessage()
    msg.hwid = b'AABBCC'
    msg.ipaddr = int(ipaddress.IPv4Address("127.0.0.1"))
    msg.name = b'test'

    data = pack_message(msg)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(data)
        sock.close()


if __name__ == "__main__":
    main()
