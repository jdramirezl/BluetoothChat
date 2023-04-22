import tkinter as tk
from tkinter import scrolledtext
import os
import pygame


def playSound(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

class GUI:
    def __init__(self, connection):
        self.connection = connection
        self.root = tk.Tk()
        self.root.title("Bluetooth Chat")
        self.message_scrolledtext = scrolledtext.ScrolledText(self.root, width=50, height=20, state='disabled')
        self.message_scrolledtext.pack(padx=10, pady=10)
        self.message_entry = tk.Entry(self.root, width=50)
        self.message_entry.pack(padx=10, pady=10)
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)
        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(padx=10, pady=10)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        pygame.init()

    def add_message(self, message, is_me=False):
        if is_me:
            playSound("./internal/assets/send.wav")
            tag = 'me'
        else:
            playSound("./internal/assets/get.wav")
            tag = 'other'
        
        self.message_scrolledtext.tag_configure('me', foreground='blue') 
        self.message_scrolledtext.configure(state='normal')
        self.message_scrolledtext.insert(tk.END, message + '\n', tag)
        self.message_scrolledtext.configure(state='disabled')

    def send_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        
        chat_message = "Me: " + message
        self.add_message(chat_message, is_me=True)
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