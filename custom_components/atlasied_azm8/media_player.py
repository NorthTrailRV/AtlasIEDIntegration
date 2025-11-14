"""Media player platform for AtlasIED AZM8."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AtlasIEDCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AtlasIED AZM8 media player platform."""
    coordinator: AtlasIEDCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create media player entities for all 8 zones
    entities = [
        AtlasIEDZone(coordinator, zone, config_entry)
        for zone in range(1, 9)
    ]

    async_add_entities(entities)


class AtlasIEDZone(CoordinatorEntity[AtlasIEDCoordinator], MediaPlayerEntity):
    """Representation of an AtlasIED AZM8 zone."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(
        self,
        coordinator: AtlasIEDCoordinator,
        zone: int,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the zone."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{config_entry.entry_id}_zone_{zone}"
        self._attr_name = f"Zone {zone}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.title,
            "manufacturer": "AtlasIED",
            "model": "AZM8",
        }
        
        # Common audio sources for the AZM8
        self._attr_source_list = [
            "Input 1",
            "Input 2",
            "Input 3",
            "Input 4",
            "Input 5",
            "Input 6",
            "Input 7",
            "Input 8",
        ]

    @property
    def zone_data(self) -> dict[str, Any]:
        """Get the data for this zone."""
        return self.coordinator.data.get(f"zone_{self._zone}", {})

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the zone."""
        if not self.zone_data.get("power", False):
            return MediaPlayerState.OFF
        if self.zone_data.get("mute", False):
            return MediaPlayerState.OFF
        return MediaPlayerState.ON

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        volume = self.zone_data.get("volume", 0)
        return volume / 100.0

    @property
    def is_volume_muted(self) -> bool | None:
        """Return True if volume is muted."""
        return self.zone_data.get("mute", False)

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        return self.zone_data.get("source")

    async def async_turn_on(self) -> None:
        """Turn the zone on."""
        await self.coordinator.set_zone_power(self._zone, True)

    async def async_turn_off(self) -> None:
        """Turn the zone off."""
        await self.coordinator.set_zone_power(self._zone, False)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        volume_int = int(volume * 100)
        await self.coordinator.set_zone_volume(self._zone, volume_int)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (True) or unmute (False) the zone."""
        await self.coordinator.set_zone_mute(self._zone, mute)

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        await self.coordinator.set_zone_source(self._zone, source)
