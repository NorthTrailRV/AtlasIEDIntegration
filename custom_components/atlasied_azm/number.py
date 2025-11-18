"""Number platform for AtlasIED AZM4/AZM8."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AZMCoordinator
from .const import CONF_NUM_SOURCES, CONF_NUM_ZONES, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AZM number entities."""
    coordinator: AZMCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    num_zones = config_entry.data.get(CONF_NUM_ZONES, 8)
    num_sources = config_entry.data.get(CONF_NUM_SOURCES, 4)
    
    # Zone gain controls
    for i in range(num_zones):
        entities.append(AZMZoneGain(coordinator, i))
    
    # Source gain controls
    for i in range(num_sources):
        entities.append(AZMSourceGain(coordinator, i))
    
    async_add_entities(entities)


class AZMNumberEntity(NumberEntity):
    """Base class for AZM number entities."""

    def __init__(self, coordinator: AZMCoordinator, param: str, name: str):
        """Initialize the number entity."""
        self._coordinator = coordinator
        self._param = param
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_{param}"
        self._attr_should_poll = False
        self._attr_mode = NumberMode.SLIDER

    async def async_added_to_hass(self) -> None:
        """Subscribe to parameter updates when added to hass."""
        await self._coordinator.subscribe_device_parameter(self._param, "pct")
        self._coordinator.subscribe_parameter(self._param, self._handle_update)
        await self._coordinator.get_parameter(self._param, "pct")

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe when removed from hass."""
        self._coordinator.unsubscribe_parameter(self._param, self._handle_update)

    def _handle_update(self) -> None:
        """Handle updates from the coordinator."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self._coordinator.get_value(self._param)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self._coordinator.set_parameter(self._param, int(value), "pct")


class AZMZoneGain(AZMNumberEntity):
    """Zone gain control (volume)."""

    def __init__(self, coordinator: AZMCoordinator, zone_idx: int):
        """Initialize zone gain control."""
        param = f"ZoneGain_{zone_idx}"
        name = f"Zone {zone_idx + 1} Volume"
        super().__init__(coordinator, param, name)
        
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = None


class AZMSourceGain(AZMNumberEntity):
    """Source gain control (volume)."""

    def __init__(self, coordinator: AZMCoordinator, source_idx: int):
        """Initialize source gain control."""
        param = f"SourceGain_{source_idx}"
        name = f"Source {source_idx + 1} Volume"
        super().__init__(coordinator, param, name)
        
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = None
