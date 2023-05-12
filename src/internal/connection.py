import socket
import threading
from .gui import GUI
import uuid
from dotenv import load_dotenv
import os


class Connection:
    backlog = 2

    def get_socket(self):  # Creates a BT socket
        s = socket.socket(self.socket_type, socket.SOCK_STREAM)
        # s.setblocking(False)
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s

    def set_bluetooth_parameter(self):
        self.self_host = os.getenv("SELFMAC")
        self.target_host = os.getenv("TARGETMAC")
        self.connection_port = os.getenv("BLUETOOTH_PORT")

    def set_tcp_parameter(self):
        self.self_host = os.getenv("SELFIP")
        self.target_host = os.getenv("TARGETIP")
        self.connection_port = int(os.getenv("TCP_PORT"))

    def set_connection(self, socket_type):
        self.bt_socket = self.get_socket()
        load_dotenv()
        # if socket_type == socket.AF_BLUETOOH:
        #     self.set_bluetooth_parameter()
        if socket_type == socket.AF_INET:
            self.set_tcp_parameter()
        if self.self_host is None or self.target_host == None or self.connection_port == None:
            raise "Socket parameters not passed"
        self.self_name = uuid.uuid4().hex[:8]

    def set_commands(self):
        load_dotenv(dotenv_path="./internal/.commands")
        self.commands = {
            "name_change": os.getenv("NAMECHANGE"),
            "disconnect": os.getenv("DISCONNECT"),
        }

    def __init__(self, socket_type):
        self.client_sockets = []
        self.socket_type = socket_type
        self.set_connection(socket_type)
        self.set_commands()

    def set_gui(self, gui):
        self.chat_gui = gui

    def set_name(self, name):
        self.self_name = name
        self.send_message(self.commands["name_change"] + self.self_name)

    def close(self):
        for client_socket in self.client_sockets:
            client_socket.close()

    def start_server(self):
        self.bt_socket.bind((self.self_host, self.connection_port))
        self.bt_socket.listen(Connection.backlog)
        port = self.bt_socket.getsockname()[1]
        self.chat_gui.add_message(
            "Waiting for incoming connections on port " + str(port) + "..."
        )

        self.accept_connections()

    def accept_connections(self):
        accept_thread = threading.Thread(target=self.receive_connections)
        accept_thread.start()

    def receive_connections(self):
        while True:
            client_socket, client_address = self.bt_socket.accept()
            self.chat_gui.add_message("Connected from " + str(client_address))
            if client_socket not in self.client_sockets:
                self.client_sockets.append(client_socket)
            self.accept_messages(client_socket)

    def accept_messages(self, client_socket):
        receive_thread = threading.Thread(
            target=self.receive_message, args=(client_socket,)
        )
        receive_thread.start()

    def client_disconnect(self, client_socket):
        self.client_sockets.remove(client_socket)
        client_socket.close()
        print("Closing connection to " + str(client_socket.getpeername()))

    def receive_message(self, client_socket):
        ChatName = "Unknown"
        while True:
            data = client_socket.recv(1024)
            data_length = data.decode().split()[0] if data is not None else None
            if data is None or data == self.commands["disconnect"]:
                self.client_disconnect()
                break
            while len(data) < data_length:
                data += client_socket.recv(1024)
            data = ' '.join(data.decode().split[1:])
            nchange = self.commands["name_change"]
            if data.startswith(nchange):
                ChatName = data.replace(nchange, "")
                continue
            self.chat_gui.add_message(ChatName + ": " + data)

    def name_check(self, name):
        if len(name) > 10:
            return False
        return True

    def send_message(self, message):
        for client_socket in self.client_sockets:
            if message.startswith(self.commands["name_change"]) and not self.name_check(
                message.replace(self.commands["name_change"], "")
            ):
                self.chat_gui.add_message("Name must be less than 10 characters")
                return

            encoded_message = bytes(message, "utf-8")
            encoded_message = bytes(str(len(encoded_message)) + " ", "utf-8") + encoded_message
            # print(encoded_message.decode())
            client_socket.send(encoded_message)

    def start_client(self):
        client_socket = self.get_socket()
        client_socket.connect((self.target_host, self.connection_port))
        self.client_sockets.append(client_socket)
        self.chat_gui.add_message("Connected to " + str(self.target_host))
        self.set_name(self.self_name)
        self.accept_messages(client_socket)
