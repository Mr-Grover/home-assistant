"""Config flow for Yale Smart Sync."""
import logging

import requests
import voluptuous as vol
from yalesmartalarmclient.client import YaleSmartAlarmClient

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import CONF_AREA, DOMAIN

_LOGGER = logging.getLogger(__name__)

REAUTH_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): str})


class YaleSmartSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Yale Smart Sync config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.username = None
        self.password = None
        self.area_id = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            # Validate user input
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            area_id = CONF_AREA

            try:
                client = await self.hass.async_add_executor_job(
                    YaleSmartAlarmClient, username, password, area_id
                )
            except requests.exceptions.HTTPError:
                errors["base"] = "invalid_auth"
                _LOGGER.error("Authentication failed. Check credentials")

            else:
                if client:
                    self.username = username
                    self.password = password
                    self.area_id = area_id

                    await self.async_set_unique_id(username)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title="Yale Smart Sync",
                        data={
                            CONF_USERNAME: self.username,
                            CONF_PASSWORD: self.password,
                        },
                    )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_reauth(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        errors = {}

        if user_input and user_input.get(CONF_USERNAME):
            self.username = user_input[CONF_USERNAME]
            self.area_id = CONF_AREA

        self.context["title_placeholders"] = {CONF_USERNAME: self.username}

        if user_input is not None and user_input.get(CONF_PASSWORD) is not None:
            try:
                await self.hass.async_add_executor_job(
                    YaleSmartAlarmClient,
                    self.username,
                    user_input[CONF_PASSWORD],
                    self.area_id,
                )
            except requests.exceptions.HTTPError:
                _LOGGER.error("Authentication failed. Check credentials")
                errors["base"] = "invalid_auth"

            entry = await self.async_set_unique_id(self.username)
            self.hass.config_entries.async_update_entry(
                entry,
                data={
                    CONF_USERNAME: self.username,
                    CONF_PASSWORD: self.password,
                },
            )

            return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth", data_schema=REAUTH_SCHEMA, errors=errors
        )
