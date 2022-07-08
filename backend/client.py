import socket
import threading


class Client:

    def __init__(self, ip, port, name=""):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, int(port)))
        if not isinstance(name, str) or name == "":
            raise Exception(f"Empty or not string username not allowed! Got: {name}")
        self.connection.send(name.encode("utf-8"))
        self.start_client()

    def _decode(self, message):
        if isinstance(message, bytes):
            return message.decode("utf-8")
        elif isinstance(message, str):
            return message.encode("utf-8")

    def start_client(self):
        print("=> Start accepting messages from server")
        self.conn = threading.Thread(target=self.receiving_messages)
        self.conn.start()
        print("=> Start sending messages to server")
        self.conn = threading.Thread(target=self.sending_messages)
        self.conn.start()

    def receiving_messages(self):
        while True:
            data_from_server = self.connection.recv(4096)
            if not data_from_server:
                break
            print(self._decode(data_from_server))

    def sending_messages(self):
        while True:
            message = input()
            if message == "exit":
                self.connection.close()
            self.connection.send(self._decode(message=message))


if __name__ == "__main__":
    host, port = input("HOST:PORT ").split(":")
    name = input("Username: ")
    client = Client(host, int(port), name)
