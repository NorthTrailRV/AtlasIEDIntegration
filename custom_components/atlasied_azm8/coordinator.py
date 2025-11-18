"""DataUpdateCoordinator for AtlasIED AZM8."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import json
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, NUM_ZONES

_LOGGER = logging.getLogger(__name__)


class AtlasIEDCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AtlasIED AZM8 data."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self._fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def _ensure_connection(self) -> None:
        """Ensure we have an active connection."""
        if self._reader is None or self._writer is None or self._writer.is_closing():
            try:
                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=10,
                )
                _LOGGER.debug("Connected to AZM8 at %s:%s", self.host, self.port)
            except Exception as err:
                _LOGGER.error("Failed to connect to AZM8: %s", err)
                raise

    async def _send_jsonrpc(self, method: str, params: dict[str, Any]) -> dict[str, Any] | None:
        """Send a JSON-RPC command and get response."""
        async with self._lock:
            try:
                await self._ensure_connection()
                
                # Build JSON-RPC message
                message = {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                }
                
                # Send message with newline delimiter
                json_str = json.dumps(message) + "\n"
                self._writer.write(json_str.encode())
                await self._writer.drain()
                
                # Read response
                response_data = await asyncio.wait_for(
                    self._reader.readline(),
                    timeout=5,
                )
                
                if not response_data:
                    raise UpdateFailed("No response from device")
                
                response = json.loads(response_data.decode().strip())
                return response
                
            except asyncio.TimeoutError as err:
                _LOGGER.error("Timeout communicating with AZM8")
                await self._close_connection()
                raise UpdateFailed("Timeout communicating with device") from err
            except Exception as err:
                _LOGGER.error("Error sending JSON-RPC: %s", err)
                await self._close_connection()
                raise UpdateFailed(f"Communication error: {err}") from err

    async def _close_connection(self) -> None:
        """Close the connection."""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as err:
                _LOGGER.debug("Error closing connection: %s", err)
        self._reader = None
        self._writer = None

    async def _get_parameter(self, param: str, fmt: str = "val") -> Any:
        """Get a single parameter value."""
        response = await self._send_jsonrpc(
            "get",
            {"param": param, "fmt": fmt}
        )
        
        if response and "params" in response and len(response["params"]) > 0:
            param_data = response["params"][0]
            if fmt in param_data:
                return param_data[fmt]
            elif "val" in param_data:
                return param_data["val"]
        
        return None

    async def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        zones_data = {}
        
        # Fetch status for all zones
        for zone_index in range(NUM_ZONES):
            try:
                # Get gain (volume in dB)
                gain = await self._get_parameter(f"ZoneGain_{zone_index}")
                
                # Get mute status
                mute = await self._get_parameter(f"ZoneMute_{zone_index}")
                
                # Get source selection
                source = await self._get_parameter(f"ZoneSource_{zone_index}")
                
                # Get zone name
                name = await self._get_parameter(f"ZoneName_{zone_index}", "str")
                
                zones_data[f"zone_{zone_index}"] = {
                    "gain": float(gain) if gain is not None else -80.0,
                    "mute": bool(int(mute)) if mute is not None else True,
                    "source": int(source) if source is not None else 0,
                    "name": name if name else f"Zone {zone_index + 1}",
                }
                
            except Exception as err:
                _LOGGER.warning("Failed to fetch zone %s data: %s", zone_index, err)
                zones_data[f"zone_{zone_index}"] = {
                    "gain": -80.0,
                    "mute": True,
                    "source": 0,
                    "name": f"Zone {zone_index + 1}",
                }
        
        return zones_data

    async def set_zone_gain(self, zone_index: int, gain: float) -> None:
        """Set zone gain level in dB."""
        try:
            await self._send_jsonrpc(
                "set",
                {"param": f"ZoneGain_{zone_index}", "val": gain}
            )
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set zone %s gain to %s: %s", zone_index, gain, err)

    async def set_zone_mute(self, zone_index: int, mute: bool) -> None:
        """Set zone mute state."""
        try:
            await self._send_jsonrpc(
                "set",
                {"param": f"ZoneMute_{zone_index}", "val": 1 if mute else 0}
            )
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set zone %s mute to %s: %s", zone_index, mute, err)

    async def set_zone_source(self, zone_index: int, source: int) -> None:
        """Set zone audio source (0-based index)."""
        try:
            await self._send_jsonrpc(
                "set",
                {"param": f"ZoneSource_{zone_index}", "val": source}
            )
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set zone %s source to %s: %s", zone_index, source, err)

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and close connection."""
        await self._close_connection()
