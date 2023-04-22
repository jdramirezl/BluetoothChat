import threading
import asyncio
from internal.gui import GUI
from bleak import BleakScanner, BleakClient
import bleak


class Connection:
    def __init__(self):
        bleak.uuids.register_uuids("e8e10f95-1a70-4b27-9ccf-02010264e9c8")
        self.charasteristic = "e8e10f95-1a70-4b27-9ccf-02010264e9c8"
    
    async def set_connection(self):
        self.chat_partner = await BleakScanner.find_device_by_address(
            "05482813-D34D-6EC0-531C-9648CC1B6F94"
        )
        async with BleakClient(self.chat_partner) as client:
            await client.connect()
            services = await client.get_services()
            for service in services:
                print(service.uuid)

    def set_gui(self, gui : GUI):
        self.chat_gui = gui
        
    async def notification_handler(self, sender, data):
        self.chat_gui.add_message(data, is_me=False)

    async def start_message_server(self):
        async with BleakClient(self.chat_partner) as client:
            await client.start_notify(self.charasteristic, self.notification_handler)
            while self.open:
                await asyncio.sleep(1)
            await client.stop_notify()


    async def send_message(self, message):
        async with BleakClient(self.chat_partner) as client:
            await client.write_gatt_char(
                self.charasteristic, message.encode()
            )

    def start(self):
        self.open = True
        threading.Thread(target=self.start_message_server)
        
    def close(self):
        self.open = False
