from internal.connection import Connection
from internal.gui import GUI

def main():
    connection = Connection()
    chat_gui = GUI(connection)
    connection.set_gui(chat_gui)
    connection.start_server()
    chat_gui.start()
    

if __name__ == "__main__":
    main()