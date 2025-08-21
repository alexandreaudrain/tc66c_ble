from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .bluetooth_passive import setup_passive_listener

SENSOR_TYPES = {
    "voltage": ("Voltage", "V"),
    "current": ("Current", "A"),
    "power": ("Power", "W"),
    "resistance": ("Resistance", "Ω"),
    "temperature": ("Temperature", "°C"),
    "data_plus": ("D+", "V"),
    "data_minus": ("D−", "V"),
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up TC66C sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    address = coordinator.address
    name = coordinator.name

    entities = [
        TC66CSensor(coordinator, key, label, unit, address, name)
        for key, (label, unit) in SENSOR_TYPES.items()
    ]

    diagnostic = TC66CDiagnosticSensor(name)
    entities.append(diagnostic)

    setup_passive_listener(hass, diagnostic.handle_ble_data)

    async_add_entities(entities)

class TC66CSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, key, label, unit, address, name):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.key = key
        self._attr_name = f"{name} {label}"
        self._attr_unique_id = f"{address}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_info = {
            "identifiers": {(DOMAIN, address)},
            "name": name,
            "manufacturer": "ALX_IOT",
            "model": "TC66C",
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self.key)

class TC66CDiagnosticSensor(SensorEntity):

    def __init__(self, name):
        self._attr_name = f"{name} Diagnostic"
        self._attr_unique_id = f"{name}_diagnostic"
        self._state = "En attente..."
        self._attributes = {}
        self._pending_data = []

    async def async_added_to_hass(self):
        for service_info in self._pending_data:
            self._process_ble_data(service_info)
        self._pending_data.clear()

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    @callback
    def handle_ble_data(self, service_info):
        if self.hass is None:
            self._pending_data.append(service_info)
        else:
            self._process_ble_data(service_info)

    def _process_ble_data(self, service_info):
        self._state = "Trame reçue"
        self._attributes = {
            "adresse": service_info.address,
            "nom": service_info.name,
            "rssi": service_info.rssi,
            "manufacturer_data": {
                k: v.hex() for k, v in service_info.manufacturer_data.items()
            } if service_info.manufacturer_data else {},
            "service_data": {
                k: v.hex() for k, v in service_info.service_data.items()
            } if service_info.service_data else {},
        }
        self.async_write_ha_state()