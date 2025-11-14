"""DataUpdateCoordinator for AtlasIED AZM8."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AtlasIEDCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AtlasIED AZM8 data."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            async with async_timeout.timeout(10):
                return await self._fetch_data()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        zones_data = {}
        
        async with aiohttp.ClientSession() as session:
            # Fetch status for all 8 zones
            for zone in range(1, 9):
                try:
                    zone_data = await self._get_zone_status(session, zone)
                    zones_data[f"zone_{zone}"] = zone_data
                except Exception as err:
                    _LOGGER.warning("Failed to fetch zone %s data: %s", zone, err)
                    zones_data[f"zone_{zone}"] = {
                        "power": False,
                        "volume": 0,
                        "mute": True,
                        "source": None,
                    }
        
        return zones_data

    async def _get_zone_status(self, session: aiohttp.ClientSession, zone: int) -> dict[str, Any]:
        """Get status for a specific zone."""
        # This is a generic implementation - adjust based on actual AZM8 API
        # The AZM8 typically uses HTTP GET/POST requests for control
        
        url = f"{self.base_url}/zone{zone}/status"
        
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "power": data.get("power", False),
                    "volume": data.get("volume", 0),
                    "mute": data.get("mute", False),
                    "source": data.get("source"),
                }
            else:
                # Return default values if unable to fetch
                return {
                    "power": False,
                    "volume": 0,
                    "mute": True,
                    "source": None,
                }

    async def set_zone_power(self, zone: int, power: bool) -> None:
        """Set zone power state."""
        url = f"{self.base_url}/zone{zone}/power"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"power": power}) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to set zone %s power to %s", zone, power)
        await self.async_request_refresh()

    async def set_zone_volume(self, zone: int, volume: int) -> None:
        """Set zone volume level (0-100)."""
        url = f"{self.base_url}/zone{zone}/volume"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"volume": volume}) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to set zone %s volume to %s", zone, volume)
        await self.async_request_refresh()

    async def set_zone_mute(self, zone: int, mute: bool) -> None:
        """Set zone mute state."""
        url = f"{self.base_url}/zone{zone}/mute"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"mute": mute}) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to set zone %s mute to %s", zone, mute)
        await self.async_request_refresh()

    async def set_zone_source(self, zone: int, source: str) -> None:
        """Set zone audio source."""
        url = f"{self.base_url}/zone{zone}/source"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"source": source}) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to set zone %s source to %s", zone, source)
        await self.async_request_refresh()
