import socket
import threading
from .gui import GUI 



class Connection:
    def __init__(self):
        self.client_sockets = []
    
    def set_server_socket(self):
        self.start_server()
    
    def set_gui(self, gui):
        self.chat_gui = gui

    def send_message(self, message):
        for client_socket in self.client_sockets:
            encoded_message = bytes(message, "utf-8")
            client_socket.send(encoded_message)

    def receive_message(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                print("Closing connection to " + str(client_socket.getpeername()))
                break
            self.chat_gui.add_message("Other: " + data.decode())

    def start_server(self):
        host_mac = "00:1A:7D:DA:71:13" # Replace with the MAC address of your Bluetooth adapter
        port = 7
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
        port = 7
        
        client_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        client_socket.connect((target_mac, port))
        self.client_sockets.append(client_socket)
        self.chat_gui.add_message("Connected to " + str(target_mac))

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.chat_gui.add_message("Connected from " + str(client_address))
            receive_thread = threading.Thread(target=self.receive_message, args=(client_socket,))
            receive_thread.start()
    
    def close(self):
        for client_socket in self.client_sockets:
            client_socket.close()

