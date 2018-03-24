import socket
import ipaddress
import sys
import argparse
import ssl

from homeserver.homeprotocol.messages import pack_message
from homeserver.homeprotocol.messages import RequestConfigurationMessage

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Hostname or IP address of HomeServer")
    parser.add_argument("port", type=int, help="Service port number")
    parser.add_argument("--ssl", dest="ssl", action="store_true", help="Use SSL for connection")
    parser.add_argument("--ssl-cacert", dest="ssl_cacert", help="SSL CA Certificate")
    args = parser.parse_args()

    host = args.host
    port = args.port

    msg = RequestConfigurationMessage()
    msg.hwid = b'AABBCC'
    msg.ipaddr = int(ipaddress.IPv4Address("127.0.0.1"))
    msg.name = b'test'

    data = pack_message(msg)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if args.ssl:
        sock = ssl.wrap_socket(sock, ca_certs=args.ssl_cacert, cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_TLSv1_2)

    sock.connect((host, port))
    sock.sendall(data)
    sock.close()


if __name__ == "__main__":
    main()
