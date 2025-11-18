"""Switch platform for AtlasIED AZM4/AZM8."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AZMCoordinator
from .const import CONF_NUM_SOURCES, CONF_NUM_ZONES, CONF_NUM_GROUPS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AZM switch entities."""
    coordinator: AZMCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    num_zones = config_entry.data.get(CONF_NUM_ZONES, 8)
    num_sources = config_entry.data.get(CONF_NUM_SOURCES, 4)
    num_groups = config_entry.data.get(CONF_NUM_GROUPS, 4)
    
    # Zone mute controls
    for i in range(num_zones):
        entities.append(AZMZoneMute(coordinator, i))
    
    # Source mute controls
    for i in range(num_sources):
        entities.append(AZMSourceMute(coordinator, i))
    
    # Group active controls (Combine/Uncombine)
    for i in range(num_groups):
        entities.append(AZMGroupActive(coordinator, i))
    
    async_add_entities(entities)


class AZMSwitchEntity(SwitchEntity):
    """Base class for AZM switch entities."""

    def __init__(self, coordinator: AZMCoordinator, param: str, name: str):
        """Initialize the switch entity."""
        self._coordinator = coordinator
        self._param = param
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_{param}"
        self._attr_should_poll = False

    async def async_added_to_hass(self) -> None:
        """Subscribe to parameter updates when added to hass."""
        await self._coordinator.subscribe_device_parameter(self._param, "val")
        self._coordinator.subscribe_parameter(self._param, self._handle_update)
        await self._coordinator.get_parameter(self._param, "val")

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe when removed from hass."""
        self._coordinator.unsubscribe_parameter(self._param, self._handle_update)

    def _handle_update(self) -> None:
        """Handle updates from the coordinator."""
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        value = self._coordinator.get_value(self._param)
        return bool(value) if value is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._coordinator.set_parameter(self._param, 1, "val")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._coordinator.set_parameter(self._param, 0, "val")


class AZMZoneMute(AZMSwitchEntity):
    """Zone mute control."""

    def __init__(self, coordinator: AZMCoordinator, zone_idx: int):
        """Initialize zone mute control."""
        param = f"ZoneMute_{zone_idx}"
        name = f"Zone {zone_idx + 1} Mute"
        super().__init__(coordinator, param, name)


class AZMSourceMute(AZMSwitchEntity):
    """Source mute control."""

    def __init__(self, coordinator: AZMCoordinator, source_idx: int):
        """Initialize source mute control."""
        param = f"SourceMute_{source_idx}"
        name = f"Source {source_idx + 1} Mute"
        super().__init__(coordinator, param, name)


class AZMGroupActive(AZMSwitchEntity):
    """Group active control (Combine/Uncombine zones)."""

    def __init__(self, coordinator: AZMCoordinator, group_idx: int):
        """Initialize group active control."""
        param = f"GroupActive_{group_idx}"
        name = f"Group {group_idx + 1} Active"
        super().__init__(coordinator, param, name)
