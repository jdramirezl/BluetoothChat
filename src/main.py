from internal.connection import Connection
from internal.gui import GUI
import asyncio

async def main():
    connection = Connection()
    await connection.set_connection()
    # chat_gui = GUI(connection)
    # connection.set_gui(chat_gui)
    # connection.start()
    await connection.send_message("Hi")
    # chat_gui.start()
    

if __name__ == "__main__":
    asyncio.run(main())