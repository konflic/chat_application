import sys

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, \
    QPushButton, QListWidget, QVBoxLayout, QWidget, QLabel, QLineEdit
from backend.client import Client


class ClientGUI(QMainWindow):
    client = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Not connected")

        # Initialize widgets
        self.server_address = QLineEdit("0.0.0.0:8888")
        self.server_address.setInputMask('000.000.000.000:0000')
        self.user_name = QLineEdit()
        self.user_name.setPlaceholderText("Username")
        self.connect_button = QPushButton("Connect")
        self.send_button = QPushButton("Send")
        self.message_list = QListWidget()
        self.message_box = QLineEdit()
        self.connect_button.clicked.connect(self.connect_to_server)

        # Setting layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.server_address)
        self.layout.addWidget(self.user_name)
        self.layout.addWidget(self.connect_button)
        self.layout.addWidget(QLabel("Messages:"))
        self.layout.addWidget(self.message_list)
        self.layout.addWidget(QLabel("Say:"))
        self.layout.addWidget(self.message_box)
        self.layout.addWidget(self.send_button)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.setIcon()

    def setIcon(self):
        appIcon = QIcon("icons/client.png")
        self.setWindowIcon(appIcon)

    def connect_to_server(self):
        ip, port = self.server_address.text().split(":")
        username = self.user_name.text()
        self.client = Client(ip=ip, port=port, name=username, client_gui=self)
        self.client.start()

    def set_disconnected(self):
        self.setWindowTitle("Not connected")
        self.connect_button.setText("Connect")
        self.connect_button.clicked.connect(self.connect_to_server)
        self.send_button.clicked.connect(None)

    def set_connected(self):
        self.setWindowTitle("Connected!")
        self.connect_button.setText("Disconnect")
        self.connect_button.clicked.connect(self.disconnect)
        self.send_button.clicked.connect(self.send_message)

    def disconnect(self):
        self.client.connection.close()
        self.set_disconnected()
        self.setWindowTitle("Disconnected!")

    def add_message(self, message):
        self.message_list.addItem(message)

    def send_message(self):
        self.client.send_message()


app = QApplication(sys.argv)
window = ClientGUI()
window.show()
app.exec_()
