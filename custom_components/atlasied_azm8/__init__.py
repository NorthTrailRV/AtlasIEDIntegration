"""The AtlasIED AZM8 integration.""""""The AtlasIED AZM8 integration."""

from __future__ import annotationsfrom __future__ import annotations



import loggingimport logging

from typing import Any

from homeassistant.config_entries import ConfigEntry

from homeassistant.const import CONF_HOST, Platformfrom homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistantfrom homeassistant.const import CONF_HOST, Platform

from homeassistant.exceptions import ConfigEntryNotReadyfrom homeassistant.core import HomeAssistant

from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, DEFAULT_PORT

from .coordinator import AtlasIEDCoordinatorfrom .const import DOMAIN, DEFAULT_PORT

from .coordinator import AtlasIEDCoordinator

_LOGGER = logging.getLogger(__name__)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]



async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    """Set up AtlasIED AZM8 from a config entry."""async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    host = entry.data[CONF_HOST]    """Set up AtlasIED AZM8 from a config entry."""

    port = DEFAULT_PORT  # Always use the fixed port    host = entry.data[CONF_HOST]

    port = DEFAULT_PORT  # Always use the fixed port

    coordinator = AtlasIEDCoordinator(hass, host, port)

    coordinator = AtlasIEDCoordinator(hass, host, port)

    try:

        await coordinator.async_config_entry_first_refresh()    try:

    except Exception as err:        await coordinator.async_config_entry_first_refresh()

        raise ConfigEntryNotReady(f"Unable to connect to AtlasIED AZM8 at {host}:{port}") from err    except Exception as err:

        raise ConfigEntryNotReady(f"Unable to connect to AtlasIED AZM8 at {host}:{port}") from err

    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = coordinator    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

    return True



async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    """Unload a config entry."""async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):    """Unload a config entry."""

        coordinator = hass.data[DOMAIN].pop(entry.entry_id)    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):

        await coordinator.async_shutdown()        coordinator = hass.data[DOMAIN].pop(entry.entry_id)

        await coordinator.async_shutdown()

    return unload_ok

    return unload_ok
