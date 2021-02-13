import socket
import threading

from collections import namedtuple

User = namedtuple('User', 'username, socket_id, connection')


class Server:
    server = None
    users = []

    def __init__(self, ip, port, con_limit=5, server_gui=None, server_name="Test Server"):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(con_limit)
        self.server_gui = server_gui
        self.server_name = server_name

    def __decoder(self, message):
        if isinstance(message, bytes):
            return message.decode("utf-8")
        elif isinstance(message, str):
            return message.encode("utf-8")

    def username_taken(self, username):
        print(f"Check {username}")
        taken_names = ["server", self.server_name]
        taken_names.extend([user.username for user in self.users])
        print(taken_names)
        return username in taken_names

    def start_server(self):
        """Start accepting connections from client"""
        con = threading.Thread(target=self.accept_clients, args=(self.server,))
        con.start()

    def add_client(self, client: namedtuple):
        self.users.append(client)

    def stop_server(self):
        self.server.close()

    def send_all(self, message, excluding=None):
        if excluding is None: excluding = []
        message = self.__decoder(message)

        for client in self.users:
            if client.username not in excluding:
                client.connection.send(message)

    def accept_clients(self, the_server):
        while True:
            client, address = the_server.accept()
            # use a thread so as not to clog the gui thread
            con = threading.Thread(target=self.send_receive_client_message, args=(client, address))
            con.start()

    def send_receive_client_message(self, client_connection, client_addr):
        client_name = self.__decoder(client_connection.recv(4096))

        if self.username_taken(client_name) or client_name == "":
            client_connection.send(self.__decoder(f"server: You can't connect with this username: {client_name}!"))
            client_connection.close()
            return None

        client_connection.send(self.__decoder(f"server: Hey, {client_name}, welcome to '{self.server_name}'."))
        self.add_client(User(username=client_name, socket_id=client_addr, connection=client_connection))
        self.update_client_names_display()
        self.send_all(f"server: We got '{client_name}' connected to chat!", excluding=[client_name])

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
        del self.users[idx]

        client_connection.send(self.__decoder("server: BYE!"))
        client_connection.close()

        self.update_client_names_display()

    def get_client(self, client_list, target_connection):
        """Getting client index by connection"""
        for index, client in enumerate(client_list):
            if client.connection == target_connection:
                return index

    def update_client_names_display(self):
        """Update connected clients list"""
        self.server_gui.update_client_list(self.users)
