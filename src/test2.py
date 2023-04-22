import asyncio
from bleak import BleakScanner, BleakClient

MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"

async def main():
    device = await BleakScanner.find_device_by_address("05482813-D34D-6EC0-531C-9648CC1B6F94")
    print(device)
    async with BleakClient(device) as client:
        print(device.details)
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

asyncio.run(main())