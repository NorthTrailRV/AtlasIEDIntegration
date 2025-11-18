"""Config flow for AtlasIED AZM4/AZM8 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .azm_client import AZMClient
from .const import (
    CONF_NUM_GROUPS,
    CONF_NUM_SOURCES,
    CONF_NUM_ZONES,
    DEFAULT_NUM_GROUPS,
    DEFAULT_NUM_SOURCES,
    DEFAULT_NUM_ZONES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NUM_ZONES, default=DEFAULT_NUM_ZONES): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=16)
        ),
        vol.Optional(CONF_NUM_SOURCES, default=DEFAULT_NUM_SOURCES): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=16)
        ),
        vol.Optional(CONF_NUM_GROUPS, default=DEFAULT_NUM_GROUPS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=8)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    client = AZMClient(data[CONF_HOST])

    if not await client.connect():
        raise CannotConnect

    await client.disconnect()

    return {"title": f"AZM Device ({data[CONF_HOST]})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AtlasIED AZM."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
