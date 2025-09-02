import asyncio
import re
import sys
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from pprint import pprint
from protocol import parse


MAC_ADDRESS_FORMAT = re.compile(r"[0-9A-F]{2}(:[0-9A-F]{2}){5}")
INITIALISE_MESSAGE = (
    b"\xa1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01"
)
HISTORY_REQUEST_MESSAGE = b"\xc1"


async def main():
    address = sys.argv[1].upper() if len(sys.argv) > 1 else ""

    if not MAC_ADDRESS_FORMAT.fullmatch(address):
        print("Invalid MAC address.")
        sys.exit(1)

    while True:
        disconnect_event = asyncio.Event()

        def on_disconnect(client: BleakClient):
            disconnect_event.set()

        def on_notify(characteristic: BleakGATTCharacteristic, message: bytearray):
            try:
                pprint(parse(characteristic.uuid, message))

            except:
                print("Failed to parse message:", message.hex(" "))

        try:
            print("Attempting to connect...")

            async with BleakClient(address, on_disconnect) as client:
                print("Connected successfully.")

                await client.start_notify("2A59", on_notify)  # pyright: ignore[reportUnknownMemberType]
                await client.start_notify("2A5A", on_notify)  # pyright: ignore[reportUnknownMemberType]

                await client.write_gatt_char("2A58", INITIALISE_MESSAGE)
                await client.write_gatt_char("2A5A", HISTORY_REQUEST_MESSAGE)

                await disconnect_event.wait()

                print("Lost connection.")

        except asyncio.CancelledError:
            break

        except Exception as exception:
            print("An error occurred:", str(exception) or type(exception).__name__)

        await asyncio.sleep(5)


try:
    asyncio.run(main())

except KeyboardInterrupt:
    pass
