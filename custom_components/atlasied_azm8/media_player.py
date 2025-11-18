"""Media player platform for AtlasIED AZM8.""""""Media player platform for AtlasIED AZM8."""

from __future__ import annotationsfrom __future__ import annotations



import loggingimport logging

from typing import Anyfrom typing import Any



from homeassistant.components.media_player import (from homeassistant.components.media_player import (

    MediaPlayerEntity,    MediaPlayerEntity,

    MediaPlayerEntityFeature,    MediaPlayerEntityFeature,

    MediaPlayerState,    MediaPlayerState,

))

from homeassistant.config_entries import ConfigEntryfrom homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistantfrom homeassistant.core import HomeAssistant

from homeassistant.helpers.entity_platform import AddEntitiesCallbackfrom homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import CoordinatorEntityfrom homeassistant.helpers.update_coordinator import CoordinatorEntity



from .const import DOMAINfrom .const import DOMAIN

from .coordinator import AtlasIEDCoordinatorfrom .coordinator import AtlasIEDCoordinator



_LOGGER = logging.getLogger(__name__)_LOGGER = logging.getLogger(__name__)





async def async_setup_entry(async def async_setup_entry(

    hass: HomeAssistant,    hass: HomeAssistant,

    config_entry: ConfigEntry,    config_entry: ConfigEntry,

    async_add_entities: AddEntitiesCallback,    async_add_entities: AddEntitiesCallback,

) -> None:) -> None:

    """Set up the AtlasIED AZM8 media player platform."""    """Set up the AtlasIED AZM8 media player platform."""

    coordinator: AtlasIEDCoordinator = hass.data[DOMAIN][config_entry.entry_id]    coordinator: AtlasIEDCoordinator = hass.data[DOMAIN][config_entry.entry_id]



    # Create media player entities for all 8 zones (0-indexed)    # Create media player entities for all 8 zones (0-indexed)

    entities = [    entities = [

        AtlasIEDZone(coordinator, zone_index, config_entry)        AtlasIEDZone(coordinator, zone_index, config_entry)

        for zone_index in range(8)        for zone_index in range(8)

    ]    ]



    async_add_entities(entities)    async_add_entities(entities)





class AtlasIEDZone(CoordinatorEntity[AtlasIEDCoordinator], MediaPlayerEntity):class AtlasIEDZone(CoordinatorEntity[AtlasIEDCoordinator], MediaPlayerEntity):

    """Representation of an AtlasIED AZM8 zone."""    """Representation of an AtlasIED AZM8 zone."""



    _attr_has_entity_name = True    _attr_has_entity_name = True

    _attr_supported_features = (    _attr_supported_features = (

        MediaPlayerEntityFeature.VOLUME_SET        MediaPlayerEntityFeature.VOLUME_SET

        | MediaPlayerEntityFeature.VOLUME_MUTE        | MediaPlayerEntityFeature.VOLUME_MUTE

        | MediaPlayerEntityFeature.TURN_ON        | MediaPlayerEntityFeature.TURN_ON

        | MediaPlayerEntityFeature.TURN_OFF        | MediaPlayerEntityFeature.TURN_OFF

        | MediaPlayerEntityFeature.SELECT_SOURCE        | MediaPlayerEntityFeature.SELECT_SOURCE

    )    )



    def __init__(    def __init__(

        self,        self,

        coordinator: AtlasIEDCoordinator,        coordinator: AtlasIEDCoordinator,

        zone_index: int,        zone_index: int,

        config_entry: ConfigEntry,        config_entry: ConfigEntry,

    ) -> None:    ) -> None:

        """Initialize the zone."""        """Initialize the zone."""

        super().__init__(coordinator)        super().__init__(coordinator)

        self._zone_index = zone_index  # 0-based index        self._zone_index = zone_index  # 0-based index

        self._attr_unique_id = f"{config_entry.entry_id}_zone_{zone_index}"        self._attr_unique_id = f"{config_entry.entry_id}_zone_{zone_index}"

        self._attr_name = f"Zone {zone_index + 1}"        self._attr_name = f"Zone {zone_index + 1}"

        self._attr_device_info = {        self._attr_device_info = {

            "identifiers": {(DOMAIN, config_entry.entry_id)},            "identifiers": {(DOMAIN, config_entry.entry_id)},

            "name": config_entry.title,            "name": config_entry.title,

            "manufacturer": "AtlasIED",            "manufacturer": "AtlasIED",

            "model": "AZM8",            "model": "AZM8",

        }        }

                

        # Audio sources for the AZM8 (0-based indexing)        # Audio sources for the AZM8 (0-based indexing)

        self._attr_source_list = [        self._attr_source_list = [

            "Source 0",            "Source 0",

            "Source 1",             "Source 1", 

            "Source 2",            "Source 2",

            "Source 3",            "Source 3",

            "Source 4",            "Source 4",

            "Source 5",            "Source 5",

            "Source 6",            "Source 6",

            "Source 7",            "Source 7",

        ]        ]



    @property    @property

    def zone_data(self) -> dict[str, Any]:    def zone_data(self) -> dict[str, Any]:

        """Get the data for this zone."""        """Get the data for this zone."""

        return self.coordinator.data.get(f"zone_{self._zone_index}", {})        return self.coordinator.data.get(f"zone_{self._zone_index}", {})



    @property    @property

    def state(self) -> MediaPlayerState:    def state(self) -> MediaPlayerState:

        """Return the state of the zone."""        """Return the state of the zone."""

        if self.zone_data.get("mute", True):        if self.zone_data.get("mute", True):

            return MediaPlayerState.OFF            return MediaPlayerState.OFF

        # Zone is on if not muted and gain is above minimum        # Zone is on if not muted and gain is above minimum

        if self.zone_data.get("gain", -80.0) > -80.0:        if self.zone_data.get("gain", -80.0) > -80.0:

            return MediaPlayerState.ON            return MediaPlayerState.ON

        return MediaPlayerState.OFF        return MediaPlayerState.OFF



    @property    @property

    def volume_level(self) -> float | None:    def volume_level(self) -> float | None:

        """Volume level of the media player (0..1)."""        """Volume level of the media player (0..1)."""

        # Convert dB gain to 0-1 scale        # Convert dB gain to 0-1 scale

        # AZM8 typically ranges from -80 dB to +10 dB        # AZM8 typically ranges from -80 dB to +10 dB

        gain_db = self.zone_data.get("gain", -80.0)        gain_db = self.zone_data.get("gain", -80.0)

        # Map -80 to 0.0, 0 to ~0.89, +10 to 1.0        # Map -80 to 0.0, 0 to ~0.89, +10 to 1.0

        volume = (gain_db + 80.0) / 90.0        volume = (gain_db + 80.0) / 90.0

        return max(0.0, min(1.0, volume))        return max(0.0, min(1.0, volume))



    @property    @property

    def is_volume_muted(self) -> bool | None:    def is_volume_muted(self) -> bool | None:

        """Return True if volume is muted."""        """Return True if volume is muted."""

        return self.zone_data.get("mute", False)        return self.zone_data.get("mute", False)



    @property    @property

    def source(self) -> str | None:    def source(self) -> str | None:

        """Return the current input source."""        """Return the current input source."""

        source_index = self.zone_data.get("source", 0)        source_index = self.zone_data.get("source", 0)

        if 0 <= source_index < len(self._attr_source_list):        if 0 <= source_index < len(self._attr_source_list):

            return self._attr_source_list[source_index]            return self._attr_source_list[source_index]

        return None        return None



    async def async_turn_on(self) -> None:    async def async_turn_on(self) -> None:

        """Turn the zone on (unmute)."""        """Turn the zone on (unmute)."""

        await self.coordinator.set_zone_mute(self._zone_index, False)        await self.coordinator.set_zone_mute(self._zone_index, False)



    async def async_turn_off(self) -> None:    async def async_turn_off(self) -> None:

        """Turn the zone off (mute)."""        """Turn the zone off (mute)."""

        await self.coordinator.set_zone_mute(self._zone_index, True)        await self.coordinator.set_zone_mute(self._zone_index, True)



    async def async_set_volume_level(self, volume: float) -> None:    async def async_set_volume_level(self, volume: float) -> None:

        """Set volume level, range 0..1."""        """Set volume level, range 0..1."""

        # Convert 0-1 scale to dB gain (-80 to +10)        # Convert 0-1 scale to dB gain (-80 to +10)

        gain_db = (volume * 90.0) - 80.0        gain_db = (volume * 90.0) - 80.0

        await self.coordinator.set_zone_gain(self._zone_index, gain_db)        await self.coordinator.set_zone_gain(self._zone_index, gain_db)



    async def async_mute_volume(self, mute: bool) -> None:    async def async_mute_volume(self, mute: bool) -> None:

        """Mute (True) or unmute (False) the zone."""        """Mute (True) or unmute (False) the zone."""

        await self.coordinator.set_zone_mute(self._zone_index, mute)        await self.coordinator.set_zone_mute(self._zone_index, mute)



    async def async_select_source(self, source: str) -> None:    async def async_select_source(self, source: str) -> None:

        """Select input source."""        """Select input source."""

        try:        try:

            source_index = self._attr_source_list.index(source)            source_index = self._attr_source_list.index(source)

            await self.coordinator.set_zone_source(self._zone_index, source_index)            await self.coordinator.set_zone_source(self._zone_index, source_index)

        except ValueError:        except ValueError:

            _LOGGER.error("Invalid source: %s", source)            _LOGGER.error("Invalid source: %s", source)

