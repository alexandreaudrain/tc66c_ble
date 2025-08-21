from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEVICE_NAMES, CONF_NAME

class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TC66 BLE dongles."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self) -> None:
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, str] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle BLE discovery."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm BLE device setup."""
        assert self._discovery_info is not None
        title = self._discovery_info.name or self._discovery_info.address

        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, title),
                data={
                    CONF_ADDRESS: self._discovery_info.address,
                    CONF_NAME: user_input.get(CONF_NAME, title),
                },
            )

        self._set_confirm_only()
        self.context["title_placeholders"] = {
            "name": title,
        }

        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=self.context["title_placeholders"],
            data_schema=vol.Schema({
                vol.Optional(CONF_NAME, default=title): str,
            }),
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manual setup via UI."""
        errors: dict[str, str] = {}
        current_ids = self._async_current_ids()

        for info in async_discovered_service_info(self.hass, connectable=True):
            if not info.name or not any(name in info.name for name in DEVICE_NAMES):
                continue
            if info.address in current_ids or info.address in self._discovered_devices:
                continue
            self._discovered_devices[info.address] = f"{info.name} ({info.address})"

        if not self._discovered_devices:
            errors["base"] = "no_devices_found"

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            name = user_input.get(CONF_NAME, self._discovered_devices.get(address, address))
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=name,
                data={
                    CONF_ADDRESS: address,
                    CONF_NAME: name,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ADDRESS): vol.In(self._discovered_devices),
                vol.Optional(CONF_NAME): str,
            }),
            errors=errors,
        )