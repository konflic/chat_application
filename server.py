import sys
import random

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget, QVBoxLayout, QWidget, QLabel
from backend.server import Server


class ServerGUI(QMainWindow):
    server = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stopped")

        self.start_button = QPushButton("Start")
        self.clients_list = QListWidget()
        self.start_button.clicked.connect(self.start_server)

        # Setting layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(QLabel("Clients:"))
        self.layout.addWidget(self.clients_list)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.setIcon()

    def setIcon(self):
        appIcon = QIcon("icons/server.png")
        self.setWindowIcon(appIcon)

    def stop_server(self):
        self.server.stop_server()
        self.server = None
        self.start_button.clicked.connect(self.start_server)
        self.start_button.setText("Start")
        self.setWindowTitle("Stopped")

    def start_server(self):
        ip, port = "0.0.0.0", random.randint(8000, 8999)
        if self.server is None:
            self.server = Server(ip, port, server_gui=self)
        self.server.start_server()
        self.start_button.setText("Stop")
        self.start_button.clicked.connect(self.stop_server)
        self.setWindowTitle(f"{ip}:{port}")

    def update_client_list(self, clients):
        self.clients_list.clear()

        for client in clients:
            self.clients_list.addItem(f"{client.username}:{client.socket_id}")


app = QApplication(sys.argv)
window = ServerGUI()
window.show()
app.exec_()
