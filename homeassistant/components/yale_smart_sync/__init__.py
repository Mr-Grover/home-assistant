"""The yale Smart Sync component."""
import logging

import requests
from yalesmartalarmclient.client import YaleSmartAlarmClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .const import CONF_AREA, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["alarm_control_panel", "lock", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up upon config entry in user interface."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    area_id = CONF_AREA

    try:
        yale_client = await hass.async_add_executor_job(
            YaleSmartAlarmClient, username, password, area_id
        )
    except requests.exceptions.HTTPError as exception:
        _LOGGER.warning(exception)
        raise ConfigEntryNotReady from exception

    if not yale_client:
        raise ConfigEntryAuthFailed

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = yale_client

    # Setup components
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
