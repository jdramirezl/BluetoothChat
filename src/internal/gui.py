import tkinter as tk
from tkinter import scrolledtext

class GUI:
    def __init__(self, connection):
        self.connection = connection
        self.root = tk.Tk()
        self.root.title("Bluetooth Chat")
        self.message_listbox = tk.Listbox(self.root, width=50, height=20)
        self.message_listbox.pack(padx=10, pady=10)
        self.message_entry = tk.Entry(self.root, width=50)
        self.message_entry.pack(padx=10, pady=10)
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)
        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(padx=10, pady=10)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def add_message(self, message):
        self.message_listbox.insert(tk.END, message)

    def send_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        self.connection.send_message(message)

    def connect_to_server(self):
        self.connection.start_client()

    def receive_messages(self):
        while True:
            message = self.connection.client_socket.recv(1024).decode()
            self.add_message(message)

    def close(self):
        self.connection.close()
        self.root.destroy()
    
    def start(self):
        self.root.mainloop()