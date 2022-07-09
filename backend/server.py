import socket
import threading
import logging

from models.User import User
from collections import namedtuple


class Server:
    server = None
    users = []

    def __init__(self, ip, port, con_limit=5, server_name="Test Server"):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(con_limit)
        self.server_name = server_name
        self.__init_logger()

    def _decode(self, message):
        if isinstance(message, bytes):
            return message.decode("utf-8")
        elif isinstance(message, str):
            return message.encode("utf-8")

    def __init_logger(self, to_file=False, to_terminal=True, log_level=logging.DEBUG):
        server_logger = logging.getLogger(__name__)
        server_logger.setLevel(log_level)
        if to_file:
            f = logging.FileHandler("logs/server.log")
            f.setFormatter(logging.Formatter('%(asctime)s:%(threadName)s:%(name)s:%(levelname)s:%(message)s'))
            server_logger.addHandler(f)
        if to_terminal:
            st_h = logging.StreamHandler()
            server_logger.addHandler(st_h)
        self.logger = server_logger

    def is_username_taken(self, username):
        self.logger.info(f"=> Check if username: {username} already taken")
        taken_names = ["server", self.server_name]
        taken_names.extend([user.username for user in self.users])
        return username in taken_names

    def start_server(self):
        self.logger.info(f"=> Server {self.server_name} started!")
        con = threading.Thread(target=self.accept_clients, args=())
        con.start()

    def add_client(self, client: namedtuple):
        self.logger.info(f"=> Add client: {client} to users list")
        self.users.append(client)

    def stop_server(self):
        self.logger.info(f"=> Stop server")
        self.server.close()

    def send_all(self, message, excluding=None):
        if excluding is None:
            excluding = []

        message = self._decode(message)
        self.logger.info(f"=> Sending {message} to all clients excluding {excluding}")

        for client in self.users:
            if client.username not in excluding:
                client.connection.send(message)

    def accept_clients(self):
        self.logger.info(f"=> Start accepting client connections")
        while True:
            client, address = self.server.accept()
            self.logger.info(f"=> Got connection request from {client}:{address} started!")
            con = threading.Thread(target=self.client_messages_loop, args=(client, address))
            con.start()

    def client_messages_loop(self, client_conn, client_addr):
        client_name = self._decode(client_conn.recv(4096))
        self.logger.info(f"=> Got client name on connection: '{client_name}'")

        if self.is_username_taken(client_name) or client_name == "":
            client_conn.send(
                self._decode(f"{self.server_name}: You can't connect with username: {client_name}!"))
            client_conn.close()
            return None

        client_conn.send(self._decode(f"{self.server_name}: Hey, {client_name}, welcome to '{self.server_name}'"))

        self.add_client(
            User(
                username=client_name,
                socket_id=client_addr,
                connection=client_conn
            )
        )

        self.send_all(f"{self.server_name}: We got '{client_name}' connected to chat!", excluding=[client_name])

        while True:
            client_msg = self._decode(
                client_conn.recv(4096)
            )

            if not client_msg:
                break

            self.logger.info(f"=> Got msg {client_msg} from {client_name}")

            if client_msg == "exit":
                break

            client_index = self.get_client_connection_index(self.users, client_conn)
            sender_name = self.users[client_index].username

            self.send_all(message=f"{sender_name}: {client_msg}", excluding=[sender_name])

        client_index = self.get_client_connection_index(self.users, client_conn)

        if client_index is not None:
            self.logger.info(f"=> Delete client connection {client_index} from connections list")
            del self.users[client_index]
            client_conn.send(self._decode(f"{self.server_name}: BYE!"))
            client_conn.close()

    def get_client_connection_index(self, client_list, target_connection):
        for index, client in enumerate(client_list):
            if client.connection == target_connection:
                return index


if __name__ == "__main__":
    import random

    HOST = "0.0.0.0"
    PORT = random.randint(10000, 65535)
    server = Server(HOST, PORT)
    server.logger.info("Started server on: {}:{}".format(HOST, PORT))
    server.accept_clients()
