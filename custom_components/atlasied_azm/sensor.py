"""Sensor platform for AtlasIED AZM4/AZM8."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
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
    """Set up AZM sensor entities."""
    coordinator: AZMCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    num_zones = config_entry.data.get(CONF_NUM_ZONES, 8)
    num_sources = config_entry.data.get(CONF_NUM_SOURCES, 4)
    
    # Zone names
    for i in range(num_zones):
        entities.append(AZMZoneName(coordinator, i))
    
    # Source names
    for i in range(num_sources):
        entities.append(AZMSourceName(coordinator, i))
    
    # Zone meters
    for i in range(num_zones):
        entities.append(AZMZoneMeter(coordinator, i))
    
    # Source meters
    for i in range(num_sources):
        entities.append(AZMSourceMeter(coordinator, i))
    
    async_add_entities(entities)


class AZMSensorEntity(SensorEntity):
    """Base class for AZM sensor entities."""

    def __init__(self, coordinator: AZMCoordinator, param: str, name: str, fmt: str = "val"):
        """Initialize the sensor entity."""
        self._coordinator = coordinator
        self._param = param
        self._fmt = fmt
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_{param}"
        self._attr_should_poll = False

    async def async_added_to_hass(self) -> None:
        """Subscribe to parameter updates when added to hass."""
        await self._coordinator.subscribe_device_parameter(self._param, self._fmt)
        self._coordinator.subscribe_parameter(self._param, self._handle_update)
        await self._coordinator.get_parameter(self._param, self._fmt)

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe when removed from hass."""
        self._coordinator.unsubscribe_parameter(self._param, self._handle_update)

    def _handle_update(self) -> None:
        """Handle updates from the coordinator."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | float | None:
        """Return the current value."""
        return self._coordinator.get_value(self._param)


class AZMZoneName(AZMSensorEntity):
    """Zone name sensor."""

    def __init__(self, coordinator: AZMCoordinator, zone_idx: int):
        """Initialize zone name sensor."""
        param = f"ZoneName_{zone_idx}"
        name = f"Zone {zone_idx + 1} Name"
        super().__init__(coordinator, param, name, fmt="str")


class AZMSourceName(AZMSensorEntity):
    """Source name sensor."""

    def __init__(self, coordinator: AZMCoordinator, source_idx: int):
        """Initialize source name sensor."""
        param = f"SourceName_{source_idx}"
        name = f"Source {source_idx + 1} Name"
        super().__init__(coordinator, param, name, fmt="str")


class AZMZoneMeter(AZMSensorEntity):
    """Zone meter sensor (audio level)."""

    def __init__(self, coordinator: AZMCoordinator, zone_idx: int):
        """Initialize zone meter sensor."""
        param = f"ZoneMeter_{zone_idx}"
        name = f"Zone {zone_idx + 1} Meter"
        super().__init__(coordinator, param, name, fmt="val")
        
        self._attr_native_unit_of_measurement = "dB"
        self._attr_device_class = None


class AZMSourceMeter(AZMSensorEntity):
    """Source meter sensor (audio level)."""

    def __init__(self, coordinator: AZMCoordinator, source_idx: int):
        """Initialize source meter sensor."""
        param = f"SourceMeter_{source_idx}"
        name = f"Source {source_idx + 1} Meter"
        super().__init__(coordinator, param, name, fmt="val")
        
        self._attr_native_unit_of_measurement = "dB"
        self._attr_device_class = None
