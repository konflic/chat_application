import socket
import threading


class Client:

    def __init__(self, ip, port, name=None, client_gui=None):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, int(port)))
        self.client_gui = client_gui
        if name is None or not isinstance(name, str):
            raise Exception(f"Empty or not string username not allowed! Got: {name}")
        self.connection.send(name.encode("utf-8"))

    def __decoder(self, message):
        if isinstance(message, bytes):
            return message.decode("utf-8")
        elif isinstance(message, str):
            return message.encode("utf-8")

    def start(self):
        self.conn = threading.Thread(target=self.receiving_messages)
        self.conn.start()
        self.client_gui.set_connected()

    def leave(self):
        self.connection.close()
        self.client = None
        self.client_gui.set_disconnected()

    def receiving_messages(self):
        while True:
            from_server = self.connection.recv(4096)
            if not from_server: break
            self.client_gui.add_message(self.__decoder(from_server))
        self.client_gui.set_disconnected()

    def send_message(self):
        message_text = self.client_gui.message_box.text()
        self.connection.send(self.__decoder(message_text))
        self.client_gui.message_box.clear()
