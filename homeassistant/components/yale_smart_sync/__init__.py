"""The yale Smart Sync component."""
import asyncio
import logging

import voluptuous as vol
from yalesmartalarmclient.client import AuthenticationError, YaleSmartAlarmClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import CONF_AREA, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["alarm_control_panel", "binary_sensor"]

CONFIG_SCHEMA = vol.Schema(
    vol.All(
        cv.deprecated(DOMAIN),
        {
            DOMAIN: vol.Schema(
                {
                    vol.Required(CONF_USERNAME): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                }
            )
        },
    ),
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up upon config entry in user interface."""
    conf = entry.data
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    area_id = CONF_AREA

    try:
        client = YaleSmartAlarmClient(username, password, area_id)
    except AuthenticationError:
        _LOGGER.error("Authentication failed. Check credentials")
        return

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
