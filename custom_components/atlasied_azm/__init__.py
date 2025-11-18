"""The AtlasIED AZM4/AZM8 integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .azm_client import AZMClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AtlasIED AZM from a config entry."""
    host = entry.data[CONF_HOST]

    coordinator = AZMCoordinator(hass, host)
    
    if not await coordinator.async_connect():
        raise ConfigEntryNotReady(f"Unable to connect to AZM device at {host}")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: AZMCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_disconnect()

    return unload_ok


class AZMCoordinator:
    """Coordinator to manage AZM device connection and state."""

    def __init__(self, hass: HomeAssistant, host: str):
        """Initialize the coordinator."""
        self.hass = hass
        self.host = host
        self.client = AZMClient(host, self._handle_update)
        self._data: dict[str, Any] = {}
        self._listeners: dict[str, list] = {}

    async def async_connect(self) -> bool:
        """Connect to the AZM device."""
        return await self.client.connect()

    async def async_disconnect(self):
        """Disconnect from the AZM device."""
        await self.client.disconnect()

    async def _handle_update(self, param_data: dict[str, Any]):
        """Handle parameter updates from the device."""
        param = param_data.get("param")
        if not param:
            return

        # Store the value
        for key in ("val", "pct", "str"):
            if key in param_data:
                self._data[param] = param_data[key]
                break

        # Notify listeners
        if param in self._listeners:
            for callback in self._listeners[param]:
                callback()

    def subscribe_parameter(self, param: str, callback):
        """Subscribe to parameter updates."""
        if param not in self._listeners:
            self._listeners[param] = []
        self._listeners[param].append(callback)

    def unsubscribe_parameter(self, param: str, callback):
        """Unsubscribe from parameter updates."""
        if param in self._listeners:
            try:
                self._listeners[param].remove(callback)
                if not self._listeners[param]:
                    del self._listeners[param]
            except ValueError:
                pass

    def get_value(self, param: str) -> Any:
        """Get the current value of a parameter."""
        return self._data.get(param)

    async def set_parameter(self, param: str, value: Any, fmt: str = "val") -> bool:
        """Set a parameter value."""
        return await self.client.send_set(param, value, fmt)

    async def subscribe_device_parameter(self, param: str, fmt: str = "val") -> bool:
        """Subscribe to a parameter on the device."""
        return await self.client.subscribe(param, fmt)

    async def get_parameter(self, param: str, fmt: str = "val") -> bool:
        """Get a parameter value from the device."""
        return await self.client.send_get(param, fmt)
