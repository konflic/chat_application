import socket
import threading
import logging

from models.User import User
from collections import namedtuple


class Server:
    server = None
    users = []

    def __init__(self, ip, port, con_limit=5, server_gui=None, server_name="Test Server"):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(con_limit)
        self.server_gui = server_gui
        self.server_name = server_name
        self.__init_logger()

    def __decoder(self, message):
        if isinstance(message, bytes):
            return message.decode("utf-8")
        elif isinstance(message, str):
            return message.encode("utf-8")

    def __init_logger(self):
        server_logger = logging.getLogger(__name__)
        server_logger.setLevel(logging.DEBUG)
        f = logging.FileHandler('logs/server.log')
        formatter = logging.Formatter('%(asctime)s:%(threadName)s:%(name)s:%(levelname)s:%(message)s')
        f.setFormatter(formatter)
        server_logger.addHandler(f)
        self.logger = server_logger

    def username_taken(self, username):
        self.logger.info(f"Check if username: {username} already taken")
        taken_names = ["server", self.server_name]
        taken_names.extend([user.username for user in self.users])
        return username in taken_names

    def start_server(self):
        """Start accepting connections from clients"""
        self.logger.info(f"Server {self.server_name} started!")
        con = threading.Thread(target=self.accept_clients, args=())
        con.start()

    def add_client(self, client: namedtuple):
        self.logger.info(f"Adding client: {client} to users list")
        self.users.append(client)

    def stop_server(self):
        self.logger.info(f"Sopping server")
        self.server.close()

    def send_all(self, message, excluding=None):
        if excluding is None: excluding = []
        message = self.__decoder(message)
        self.logger.info(f"Sending {message} to all clients excluding {excluding}")

        for client in self.users:
            if client.username not in excluding:
                client.connection.send(message)

    def accept_clients(self):
        self.logger.info(f"Start accepting clients connections")

        while True:
            client, address = self.server.accept()
            self.logger.info(f"Got connection request from {client}:{address} started!")
            con = threading.Thread(target=self.send_receive_client_message, args=(client, address))
            con.start()

    def send_receive_client_message(self, client_connection, client_addr):
        client_name = self.__decoder(client_connection.recv(4096))
        self.logger.info(f"Got client name on connection: '{client_name}'")

        if self.username_taken(client_name) or client_name == "":
            client_connection.send(
                self.__decoder(f"{self.server_name}: You can't connect with username: {client_name}!"))
            client_connection.close()
            return None

        client_connection.send(
            self.__decoder(f"{self.server_name}: Hey, {client_name}, welcome to '{self.server_name}'."))
        self.add_client(User(username=client_name, socket_id=client_addr, connection=client_connection))
        self.update_client_names_display()
        self.send_all(f"{self.server_name}: We got '{client_name}' connected to chat!", excluding=[client_name])

        while True:
            data = self.__decoder(client_connection.recv(4096))

            if not data: break
            if data == "exit": break

            client_msg = data
            idx = self.get_client(self.users, client_connection)
            sender_name = self.users[idx].username

            for client in self.users:
                if client.connection != client_connection:
                    client.connection.send(self.__decoder(f"{sender_name}: {client_msg}"))
                else:
                    client.connection.send(self.__decoder(f"me: {client_msg}"))

        idx = self.get_client(self.users, client_connection)

        if idx is not None:
            self.logger.info(f"Deleting client connection from connections list by index: {idx}")
            del self.users[idx]

            client_connection.send(self.__decoder(f"{self.server_name}: BYE!"))
            client_connection.close()

            self.update_client_names_display()

    def get_client(self, client_list, target_connection):
        """Getting client index by connection"""
        self.logger.info("Getting client connection index by connection.")

        for index, client in enumerate(client_list):
            if client.connection == target_connection:
                return index

    def update_client_names_display(self):
        """Update connected clients list"""
        self.logger.info(f"Calling update of clients list in GUI")
        self.server_gui.update_client_list(self.users)


if __name__ == "__main__":
    import random
    HOST = "127.0.0.1"
    PORT = random.randint(11111, 65535)
    print("Started: {}:{}".format(HOST, PORT))
    server = Server(HOST, PORT)
    server.accept_clients(server.server)
