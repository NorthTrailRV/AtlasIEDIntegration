"""Config flow for AtlasIED AZM8 integration.""""""Config flow for AtlasIED AZM8 integration."""

from __future__ import annotationsfrom __future__ import annotations



import loggingimport logging

from typing import Anyfrom typing import Any



import voluptuous as volimport voluptuous as vol



from homeassistant import config_entriesfrom homeassistant import config_entries

from homeassistant.const import CONF_HOST, CONF_NAMEfrom homeassistant.const import CONF_HOST, CONF_NAME

from homeassistant.core import HomeAssistantfrom homeassistant.core import HomeAssistant

from homeassistant.data_entry_flow import FlowResultfrom homeassistant.data_entry_flow import FlowResult

import homeassistant.helpers.config_validation as cvimport homeassistant.helpers.config_validation as cv



from .const import DOMAIN, DEFAULT_PORTfrom .const import DOMAIN, DEFAULT_PORT

from .coordinator import AtlasIEDCoordinatorfrom .coordinator import AtlasIEDCoordinator



_LOGGER = logging.getLogger(__name__)_LOGGER = logging.getLogger(__name__)



STEP_USER_DATA_SCHEMA = vol.Schema(STEP_USER_DATA_SCHEMA = vol.Schema(

    {    {

        vol.Required(CONF_HOST): cv.string,        vol.Required(CONF_HOST): cv.string,

        vol.Optional(CONF_NAME, default="AtlasIED AZM8"): cv.string,        vol.Optional(CONF_NAME, default="AtlasIED AZM8"): cv.string,

    }    }

))





async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:

    """Validate the user input allows us to connect.    """Validate the user input allows us to connect.



    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.

    """    """

    coordinator = AtlasIEDCoordinator(    coordinator = AtlasIEDCoordinator(

        hass,        hass,

        data[CONF_HOST],        data[CONF_HOST],

        DEFAULT_PORT,        DEFAULT_PORT,

    )    )



    # Test the connection    # Test the connection

    await coordinator.async_refresh()    await coordinator.async_refresh()



    if not coordinator.last_update_success:    if not coordinator.last_update_success:

        raise CannotConnect        raise CannotConnect



    # Return info that you want to store in the config entry.    # Return info that you want to store in the config entry.

    return {"title": data.get(CONF_NAME, "AtlasIED AZM8")}    return {"title": data.get(CONF_NAME, "AtlasIED AZM8")}





class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    """Handle a config flow for AtlasIED AZM8."""    """Handle a config flow for AtlasIED AZM8."""



    VERSION = 1    VERSION = 1



    async def async_step_user(    async def async_step_user(

        self, user_input: dict[str, Any] | None = None        self, user_input: dict[str, Any] | None = None

    ) -> FlowResult:    ) -> FlowResult:

        """Handle the initial step."""        """Handle the initial step."""

        errors: dict[str, str] = {}        errors: dict[str, str] = {}

        if user_input is not None:        if user_input is not None:

            try:            try:

                info = await validate_input(self.hass, user_input)                info = await validate_input(self.hass, user_input)

            except CannotConnect:            except CannotConnect:

                errors["base"] = "cannot_connect"                errors["base"] = "cannot_connect"

            except Exception:  # pylint: disable=broad-except            except Exception:  # pylint: disable=broad-except

                _LOGGER.exception("Unexpected exception")                _LOGGER.exception("Unexpected exception")

                errors["base"] = "unknown"                errors["base"] = "unknown"

            else:            else:

                await self.async_set_unique_id(                await self.async_set_unique_id(

                    f"{user_input[CONF_HOST]}:{DEFAULT_PORT}"                    f"{user_input[CONF_HOST]}:{DEFAULT_PORT}"

                )                )

                self._abort_if_unique_id_configured()                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)                return self.async_create_entry(title=info["title"], data=user_input)



        return self.async_show_form(        return self.async_show_form(

            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors

        )        )





class CannotConnect(Exception):class CannotConnect(Exception):

    """Error to indicate we cannot connect."""    """Error to indicate we cannot connect."""

