import logging
from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothServiceInfoBleak,
    async_register_callback,
    BluetoothScanningMode,
    BluetoothChange,
)
from homeassistant.core import callback
from .const import TC66C_DEVICE_NAMES

_LOGGER = logging.getLogger(__name__)

def setup_passive_listener(hass, on_data_callback):

    @callback
    def handle_ble_advertisement(service_info: BluetoothServiceInfoBleak, change: BluetoothChange):
        if not service_info.name or not service_info.address:
            return

        if not any(name in service_info.name for name in TC66C_DEVICE_NAMES):
            return

        safe_manufacturer_data = {
            k: v.hex() for k, v in service_info.manufacturer_data.items()
        } if service_info.manufacturer_data else {}

        _LOGGER.debug(
            "BLE Pub reçue : %s | Adresse : %s | Changement : %s | Manufacturer : %s",
            service_info.device.name,
            service_info.device.address,
            change,
            safe_manufacturer_data
        )

        on_data_callback(service_info)

    matcher = BluetoothCallbackMatcher()
    async_register_callback(
        hass,
        handle_ble_advertisement,
        matcher,
        BluetoothScanningMode.PASSIVE
    )