import socket
import threading
from .gui import GUI 



class Connection:
    def __init__(self):
        self.client_sockets = []
    
    def set_server_socket(self):
        self.server_socket = self.start_server()
    
    def set_gui(self, gui):
        self.chat_gui = gui

    def send_message(self, message):
        for client_socket in self.client_sockets:
            client_socket.send(message.encode())

    def receive_message(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data or (data and data.decode() == "quit"):
                break
            self.chat_gui.add_message("Other: " + data.decode())

    def start_server(self):
        host_mac = "00:1A:7D:DA:71:13" # Replace with the MAC address of your Bluetooth adapter
        port = 3
        backlog = 1
        
        self.server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.server_socket.bind((host_mac, port)) # Use any free Bluetooth port
        self.server_socket.listen(backlog)
        
        port = self.server_socket.getsockname()[1]
        self.chat_gui.add_message("Waiting for incoming connections on port " + str(port) + "...")
        
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()
    
    def start_client(self):
        target_mac = "14:F6:D8:32:D4:89" # Replace with the MAC address of your Bluetooth adapter
        port = 3
        
        self.client_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.client_socket.connect((target_mac, port))
        print(self.chat_gui, "exists")
        receive_thread = threading.Thread(target=self.chat_gui.receive_messages)
        receive_thread.start()

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.chat_gui.add_message("Connected to " + str(client_address))
            self.client_sockets.append(client_socket)
            receive_thread = threading.Thread(target=self.receive_message, args=(client_socket,))
            receive_thread.start()
    
    def close(self):
        for client_socket in self.client_sockets:
            client_socket.close()

