import asyncio
from bleak import BleakScanner
from time import sleep

async def scan_devices():
    print("Trazim BLE uredjaje...")
    scanner = BleakScanner()
    devices = await scanner.discover()

    if devices:
              print(f"Nadjeno je {len(devices)} BLE uredjaja:")
              for device in devices:
               print(f"Ime: {device.name}, MAC adresa: {device.address}, RSSI: {device.rssi}")
    else:
        print("Nije pronadjen nijedan BLE uredjaj")

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(scan_devices())
        except Exception as e:
            print("Nesto mirise na dim...")
            print({e})
            sleep(10)
     