"""Component for interacting with the Yale Smart Alarm System API."""
import logging

import voluptuous as vol
from yalesmartalarmclient.client import (
    AuthenticationError,
    YaleSmartAlarmClient,
)

from homeassistant.components.binary_sensor import (
    BinarySensorDevice,
    DEVICE_CLASS_LOCK,
    PLATFORM_SCHEMA,
)

from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
)
import homeassistant.helpers.config_validation as cv

CONF_AREA_ID = "area_id"

DEFAULT_NAME = "Yale Smart Lock"

DEFAULT_AREA_ID = "1"

DEFAULT_ICON = "mdi:lock"

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "lock": ["Locks", DEVICE_CLASS_LOCK],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_AREA_ID, default=DEFAULT_AREA_ID): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the alarm platform."""
    name = config[CONF_NAME]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    area_id = config[CONF_AREA_ID]
    device_class = DEVICE_CLASS_LOCK

    try:
        client = YaleSmartAlarmClient(username, password, area_id)
    except AuthenticationError:
        _LOGGER.error("Authentication failed. Check credentials")
        return

    add_entities([YaleAlarmDevice(name, client, device_class)], True)


class YaleAlarmDevice(BinarySensorDevice):
    """Represent a Yale Smart Sync Lock."""

    def __init__(self, name, client, device_class: str):
        """Initialize the Yale Sync Lock."""
        self._name = name
        self._client = client
        self._state = None
        self._device_class = DEVICE_CLASS_LOCK

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return DEVICE_CLASS_LOCK

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self._state

    def update(self):
        """Return the state of the device."""
        lock_status = self._client.get_locks_status()
        for name in lock_status:
            self._name = name
            self._state = lock_status[name]
