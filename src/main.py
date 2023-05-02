from internal.connection import Connection
from internal.gui import GUI
from socket import AF_INET

def main():
    connection = Connection(AF_INET)
    chat_gui = GUI(connection)
    connection.set_gui(chat_gui)
    connection.start_server()
    chat_gui.start()
    

if __name__ == "__main__":
    main()