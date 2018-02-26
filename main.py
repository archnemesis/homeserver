import argparse
import datetime
import socketserver
import socket
import threading
import ipaddress
import logging
import queue
import time
import cmd
import pymongo
from homeserver.homeprotocol import messages
from homeserver.homeprotocol.parser import Parser


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter);
logger.addHandler(ch)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, db, *args, **kwargs):
        self._threads = []
        self.db = db
        super().__init__(*args, **kwargs)

    def broadcast_message(self, message):
        for thread in self._threads:
            thread.send_message(message)

    def process_request(self, request, client_address):
        t = HomeServerTCPHandler(self.db, request, client_address)
        t.daemon = self.daemon_threads
        t.start()
        self._threads.append(t)

    def server_close(self):
        for t in self._threads:
            t.terminate_conn()
            t.join()
        super().server_close()


class HomeServerTCPHandler(threading.Thread, socketserver.BaseRequestHandler):
    def __init__(self, db, request, client_address, *args, **kwargs):
        self.db = db
        self.parser = Parser()
        self.request = request
        self.client_address = client_address
        self.message_queue = queue.Queue()
        self.running = True
        super().__init__(*args, **kwargs)

    def run(self):
        self.handle()

    def send_message(self, message):
        self.message_queue.put(message)

    def terminate_conn(self):
        self.running = False

    def handle(self):
        self.request.settimeout(1)
        timeout_counter = 0

        while self.running:
            try:
                data = self.request.recv(1024)
            except socket.timeout as e:
                timeout_counter += 1
                if timeout_counter > 30:
                    logger.info("Connection closed")
                    return
                while not self.message_queue.empty():
                    try:
                        message = self.message_queue.get(False)
                    except queue.Empty as e:
                        break
                    else:
                        self.request.sendall(messages.pack_message(message))
            except socket.error as e:
                return
            else:
                if len(data) == 0:
                    logger.info("Connection closed")
                    return
                for message in self.parser.process_bytes(data):
                    if type(message) is messages.RequestConfigurationMessage:
                        hwid = "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*message.hwid[:])
                        logger.info("Received configuration request from %s" % hwid)

                        device = self.db.device.find_one({"hwid": hwid})

                        if device is None:
                            logger.info("Device is new and unregistered, creating new device entry")

                            self.db.device.insert_one({
                                "hwid": hwid,
                                "name": "%s" % message.name.decode("ascii").strip(),
                                "description": "Unregistered device detected",
                                "device_type": 0,
                                "active": False,
                                "created": datetime.datetime.utcnow(),
                                "updated": None
                            })

                            logger.info("Sending RequestDeniedUnRegistered to device")
                            response = messages.RequestErrorMessage()
                            response.code = messages.ErrorCode.RequestDeniedUnRegistered
                            response.message = b'unregistered'
                            self.request.sendall(messages.pack_message(response))
                        elif device['active'] == False:
                            logger.info("Sending RequestDeniedUnRegistered to device")
                            response = messages.RequestErrorMessage()
                            response.code = messages.ErrorCode.RequestDeniedUnRegistered
                            response.message = b'unregistered'
                            self.request.sendall(messages.pack_message(response))
                        else:
                            logger.info("Sending configuration payload to %s" % hwid)
                            payload = messages.ConfigurationPayloadMessage()
                            payload.display_name = device['name'].encode('ascii')
                            payload.description = device['description'].encode('ascii')
                            payload.theme = messages.DeviceUITheme.Default
                            payload.controls = []
                            payload.controls.append(
                                messages.ConfigurationPayloadMessage.ConfigurationPayloadMessageControlsParam(
                                    controltype=messages.ControlType.OnOff,
                                    min=0,
                                    max=0,
                                    name="Test On/Off".encode('ascii'),
                                    description="Test On/Off".encode('ascii')
                                )
                            )
                            self.request.sendall(messages.pack_message(payload))
                    elif type(message) is messages.PingMessage:
                        logger.info("Received ping from client")
                        timeout_counter = 0

        logger.info("End connection")


class HomeConsoleShell(cmd.Cmd):
    intro = "HomeConsole Shell. Type help or ? to list commands.\n"
    prompt = "(HomeConsole) "

    def __init__(self, server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = server

    def do_send_ping(self, arg):
        """Send PING packet to node(s)"""

        if arg == "*":
            message = messages.PingMessage()
            message.timestamp = 1
            server.broadcast_message(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("address", help="Address to listen for connections on")
    parser.add_argument("port", type=int, default=2005, help="Service port number")
    args = parser.parse_args()

    address = args.address
    port = args.port

    logger.info("Connecting to MongoDB...")
    mongo = pymongo.MongoClient('mongodb', 27017)
    db = mongo['homeserver_dev']

    logger.info("Starting server on %s:%d..." % (address, port))
    server = ThreadedTCPServer(db, (address, port), HomeServerTCPHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping server (user request)...")
        server.shutdown()
        server.server_close()
        logger.info("Done")
