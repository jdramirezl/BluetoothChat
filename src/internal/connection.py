import socket
import threading
from .gui import GUI 
import uuid
from dotenv import load_dotenv
import os

class Connection:
    def __init__(self):
        # List for client connections
        self.client_sockets = []

        # Bluetooth socket for self machine. To act as server
        self.bt_socket = self.get_socket()
        
        # Load environment variables from .env file
        load_dotenv()
        self_host = os.getenv("SELFMAC")
        target_host = os.getenv("TARGETMAC")
        port = os.getenv("PORT")
        
        if self_host == None or target_host == None or port == None:
            return
        
        # Self MAC address
        self.self_host = self_host

        # Target MAC address
        self.target_host = target_host
        
        # Connection port
        self.connection_port = int(port)
        
        # Commands
        self.self_name = uuid.uuid4().hex[:8]
        self.set_commands()


    # Setters and getters
    def set_commands(self):
        self.commands = {
            'name_change': os.getenv("NAMECHANGE"),
            'disconnect': os.getenv("DISCONNECT"),
        }

    def get_socket(self): # Creates a BT socket
        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        # s.setblocking(False)
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        return s
    
    def set_gui(self, gui): # Sets the GUI
        self.chat_gui = gui
    
    def set_name(self, name): # Sets our name and sends it to the other party
        self.self_name = name
        self.send_message(self.commands['name_change'] + self.self_name)

    # BT functions --------------------------------
    # Start
    def start(self): # Starts the connection
        self.start_server()

    # Close
    def close(self):
            for client_socket in self.client_sockets:
                client_socket.close()

    # Server functions --------------------------------

    # Starts the server
    def start_server(self): 
        host_mac = self.self_host 
        port = self.connection_port
        backlog = 2 
        
        self.bt_socket.bind((host_mac, port))
        self.bt_socket.listen(backlog)

        port = self.bt_socket.getsockname()[1]
        self.chat_gui.add_message("Waiting for incoming connections on port " + str(port) + "...")
        
        self.accept_connections()

    # Creates a thread to accept incoming connections
    def accept_connections(self): 
        accept_thread = threading.Thread(target=self.receive_connections)
        accept_thread.start()
    
    # Accepts incoming connections
    def receive_connections(self): 
        while True:
            # Accepts the connection
            client_socket, client_address = self.bt_socket.accept()
            self.chat_gui.add_message("Connected from " + str(client_address))
            
            # When we accept the connection we want it to be two-way, we add it to our clients
            # If the client is not in the list, we add it
            if client_socket not in self.client_sockets:
                self.client_sockets.append(client_socket)
            
            # We create a new thread to receive messages from the client
            self.accept_messages( client_socket)

    # Create a thread to receive messages from the client
    def accept_messages(self, client_socket):
        receive_thread = threading.Thread(target=self.receive_message, args=(client_socket,))
        receive_thread.start()

    # Receives messages from an specific client
    def receive_message(self, client_socket): 
        ChatName = "Unknown"
        while True:
            data = client_socket.recv(1024) # Receives data from the client

            # If there is no data or the data is the disconnect command, we close the connection
            if not data or data.decode() == self.commands['disconnect']:
                self.client_sockets.remove(client_socket)
                client_socket.close()
                print("Closing connection to " + str(client_socket.getpeername()))
                break
            
            # If the data is a name change command, we change the name
            nchange = self.commands['name_change']
            if data.decode().startswith(nchange):
                ChatName = data.decode().replace(nchange, "")
                continue
            
            # If the data is not a name change command, we print the message
            self.chat_gui.add_message(ChatName + ": " + data.decode())

    

    # Client functions --------------------------------

    def name_check(self, name):
        
        
        if len(name) > 10:
            return False
        return True

    # Sends a message to all connections
    def send_message(self, message):
        for client_socket in self.client_sockets:
            if message.startswith(self.commands['name_change']):
                if not self.name_check(message.replace(self.commands['name_change'], "")):
                    self.chat_gui.add_message("Name must be less than 10 characters")
                    return
            
            encoded_message = bytes(message, "utf-8")
            client_socket.send(encoded_message)
    
    # Starts the client
    def start_client(self): 
        # Creates a new socket and connects to the target
        target_mac = self.target_host
        port = self.connection_port

        client_socket = self.get_socket()
        client_socket.connect((target_mac, port))
        self.client_sockets.append(client_socket)
        
        self.chat_gui.add_message("Connected to " + str(target_mac))
        self.set_name(self.self_name)
        
        # Creates a new thread to receive messages from the client
        self.accept_messages(client_socket)


