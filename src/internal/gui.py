import tkinter as tk
from tkinter import scrolledtext, ttk
import os
import pygame
from dotenv import load_dotenv


def playSound(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

class GUI:
    def set_chat_window(self, connection):
        self.connection = connection
        self.root = tk.Tk()
        self.root.title("Bluetooth Chat")
        self.message_scrolledtext = scrolledtext.ScrolledText(self.root, width=50, height=20, state='disabled')
        self.message_scrolledtext.pack(padx=10, pady=10)
        self.message_entry = tk.Entry(self.root, width=50)
        self.message_entry.pack(padx=10, pady=10)
        self.message_entry.bind("<Key>", self.handle_key)
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)
        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(padx=10, pady=10)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
    
    def __init__(self, connection):
        self.set_chat_window()
        pygame.init()
        
    def play_sound(self, is_me):
        if is_me:
            playSound("./internal/assets/send.wav")
        else:
            playSound("./internal/assets/get.wav")
            
    def format_message(self, message, is_me):
        tag = 'me' if is_me else 'other' 
        self.message_scrolledtext.tag_configure('me', foreground='blue') 
        self.message_scrolledtext.configure(state='normal')
        self.message_scrolledtext.insert(tk.END, message + '\n', tag)
        self.message_scrolledtext.configure(state='disabled')

    def add_message(self, message, is_me=False):
        self.play_sound(is_me)
        self.format_message(message, is_me)

    def handle_key(self, event):
        """
        Function bound to the <Key> event of the message entry.
        Displays a dropdown menu of possible commands if the first character of the entered text is a "/".
        """
        text = event.widget.get()
        if len(text) == 1 and text.startswith("/"):
            commands = self.get_possible_commands()
            if commands:
                menu = ttk.Combobox(self.root, values=commands)
                menu.place(x=self.message_entry.winfo_x(), y=self.message_entry.winfo_y()+self.message_entry.winfo_height())
                menu.bind("<<ComboboxSelected>>", lambda e: self.handle_command_selection(event, menu))
                menu.bind("<Escape>", lambda e: menu.destroy())
                menu.focus_set()
    
    def get_possible_commands(self):
        load_dotenv(dotenv_path='./internal/.commands')
        
        c1, c2 = os.getenv("NAMECHANGE"), os.getenv("DISCONNECT")
        
        if c1 == None or c2 == None:
            print("Error: .env file not found or missing variables")
            return []
        
        commands = [
            c1,
            c2,
        ]
        return commands

    def handle_command_selection(self, event, menu):
        """
        Function called when a command is selected from the dropdown menu.
        Replaces the entered text with the selected command.
        """
        command = menu.get()
        event.widget.delete(0, tk.END)
        event.widget.insert(0, command)
        menu.destroy()
    
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