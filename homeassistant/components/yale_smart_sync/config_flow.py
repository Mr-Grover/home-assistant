"""Config flow for Yale Smart Sync."""
import voluptuous as vol
from yalesmartalarmclient.client import YaleSmartAlarmClient

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import CONF_AREA, DOMAIN

PASSWORD_DATA_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): str})


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

            client = await self.hass.async_add_executor_job(
                YaleSmartAlarmClient, username, password, area_id
            )

            if client:
                self.username = username
                self.password = password
                self.area_id = area_id

            # authentication failed / invalid
            errors["base"] = "invalid_auth"

            await self.async_set_unique_id(username)
            self._abort_if_unique_id_configured()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME, default="UserName"): str,
                vol.Required(CONF_PASSWORD, default="Password"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_reauth(self, config):
        """Perform reauth upon an authentication error."""
        self.username = config[CONF_USERNAME]

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        errors = {}
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=PASSWORD_DATA_SCHEMA,
            )

        client = YaleSmartAlarmClient(self.username, self.password, self.area_id)

        if not client:
            errors["base"] = "invalid_auth"
            return self.async_show_form(
                step_id="reauth_confirm",
                errors=errors,
                data_schema=PASSWORD_DATA_SCHEMA,
            )

        existing_entry = await self.async_set_unique_id(self.username)
        new_entry = {
            CONF_USERNAME: self.username,
            CONF_PASSWORD: user_input[CONF_PASSWORD],
            CONF_AREA: self.area_id,
        }
        self.hass.config_entries.async_update_entry(existing_entry, data=new_entry)

        self.hass.async_create_task(
            self.hass.config_entries.async_reload(existing_entry.entry_id)
        )

        return self.async_abort(reason="reauth_successful")
