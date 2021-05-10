"""Config flow for Yale Smart Sync."""
import logging

import requests
import voluptuous as vol
from yalesmartalarmclient.client import YaleSmartAlarmClient

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME

from .const import CONF_AREA, DOMAIN

_LOGGER = logging.getLogger(__name__)

REAUTH_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): str})
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_PIN): str,
    }
)


class YaleSmartSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Yale Smart Sync config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.username = None
        self.password = None
        self.area_id = None
        self._reauth_entry = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            # Validate user input
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            area_id = CONF_AREA
            unique_id = user_input[CONF_USERNAME].lower()
            await self.async_set_unique_id(unique_id)
            if not self._reauth_entry:
                self._abort_if_unique_id_configured

            try:
                await self.hass.async_add_executor_job(
                    YaleSmartAlarmClient, username, password, area_id
                )
            except requests.exceptions.HTTPError:
                errors["base"] = "invalid_auth"
                _LOGGER.error("Authentication failed. Check credentials")

            else:
                if not self._reauth_entry:
                    return self.async_create_entry(
                        title=user_input[CONF_USERNAME], data=user_input
                    )
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data=user_input, unique_id=unique_id
                )
                # Reload the config entry otherwise devices will remain unavailable
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                )
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, user_input=None):
        """Perform reauth if the user credentials have changed."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        self._username = user_input[CONF_USERNAME]
        return await self.async_step_user()
