import logging
from Crypto.Cipher import AES
from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothServiceInfoBleak,
    async_register_callback,
)
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

AESKeySource = [
    0x58, 0x21, -0x6, 0x56, 0x1, -0x4e, -0x10, 0x26, -0x79, -0x1, 0x12,
    0x4, 0x62, 0x2a, 0x4f, -0x50, -0x7a, -0xc, 0x2, 0x60, -0x7f, 0x6f,
    -0x66, 0xb, -0x59, -0xf, 0x6, 0x61, -0x66, -0x48, 0x72, -0x78
]
AESKey = bytes([b & 0xFF for b in AESKeySource])

device_buffers: dict[str, bytearray] = {}

def decrypt(data: bytes) -> bytes:
    cipher = AES.new(AESKey, AES.MODE_ECB)
    return cipher.decrypt(data)

def parse_packet(data: bytes) -> dict:
    readings = [int.from_bytes(data[i:i+4], "little") for i in range(48, 101, 4)]
    voltage = readings[0] / 10000
    current = readings[1] / 100000
    power = readings[2] / 10000
    ohms = readings[5] / 10
    tempFlag = readings[10]
    temperature = readings[11]
    dataPlus = readings[12] / 100
    dataMinus = readings[13] / 100
    if tempFlag == 1:
        temperature = -temperature

    return {
        "voltage": voltage,
        "current": current,
        "power": power,
        "resistance": ohms,
        "temperature": temperature,
        "data_plus": dataPlus,
        "data_minus": dataMinus
    }

def decode_buffer(address: str, update_callback):
    buffer = device_buffers.get(address, bytearray())
    while len(buffer) >= 192:
        chunk = buffer[:192]
        decoded = decrypt(chunk)
        if decoded[:4] == b'pac1':
            data = parse_packet(decoded)
            _LOGGER.debug("TC66C [%s] données décodées : %s", address, data)
            update_callback(data)
            buffer = buffer[192:]
        else:
            _LOGGER.debug("TC66C [%s] trame invalide, décalage du buffer", address)
            buffer = buffer[1:]
    device_buffers[address] = buffer

def setup_ble_listener(hass: HomeAssistant, address: str, update_callback):
    matcher = BluetoothCallbackMatcher(address=address)

    @callback
    def handle_ble(service_info: BluetoothServiceInfoBleak):
        payload = service_info.manufacturer_data.get(0xFFFF)
        if not payload:
            return

        if address not in device_buffers:
            device_buffers[address] = bytearray()
        device_buffers[address].extend(payload)

        decode_buffer(address, update_callback)

    async_register_callback(hass, handle_ble, matcher, DOMAIN)