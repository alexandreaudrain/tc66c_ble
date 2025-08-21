from datetime import timedelta, datetime
import logging
import asyncio

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from bleak import BleakClient

from .bluetooth import decrypt, parse_packet

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=5)

WRITE_CHAR_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"
NOTIFY_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
GETVA_COMMAND = bytearray.fromhex("6267657476610d0a")  # "bgetva\r\n"

class TC66Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, address, name):
        super().__init__(
            hass,
            _LOGGER,
            name=f"tc66_ble_{name}",
            update_interval=SCAN_INTERVAL,
        )
        self.address = address
        self.name = name
        self.client = BleakClient(self.address)
        self.buffer = bytearray()
        self.data = {}
        self.last_update = None

    async def _async_update_data(self):
        _LOGGER.debug("Mise à jour TC66C déclenchée automatiquement")
        try:
            if not self.client.is_connected:
                await self.client.connect()
                await self.client.start_notify(NOTIFY_CHAR_UUID, self._notification_handler)
                _LOGGER.info("TC66C [%s] connecté", self.address)

            await self.client.write_gatt_char(WRITE_CHAR_UUID, GETVA_COMMAND)
            await asyncio.sleep(1.2)

            self.last_update = datetime.now()

            return self._decode_buffer()

        except Exception as err:
            _LOGGER.warning("TC66C [%s] erreur BLE : %s", self.address, err)
            raise UpdateFailed(f"Erreur mise à jour TC66C : {err}") from err

    def _notification_handler(self, sender, data):
        _LOGGER.debug("TC66C [%s] trame reçue : %s", self.address, data.hex())
        self.buffer.extend(data)

    def _decode_buffer(self):
        while len(self.buffer) >= 192:
            chunk = self.buffer[:192]
            decrypted = decrypt(chunk)
            if decrypted[:4] == b'pac1':
                parsed = parse_packet(decrypted)
                self.buffer = self.buffer[192:]
                self.data = parsed
                return parsed
            else:
                self.buffer = self.buffer[1:]

        raise UpdateFailed("Aucune trame valide décodée")