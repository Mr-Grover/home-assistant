"""Support for Yale lock."""
import logging

from homeassistant.components.lock import LockEntity
from homeassistant.const import CONF_PIN

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Yale locks."""

    pin = config_entry.data[CONF_PIN]

    locks = []

    client = hass.data[DOMAIN][config_entry.entry_id]

    lock_name = await hass.async_add_executor_job(client.get_locks_status)
    for lock_name in lock_name.keys():
        lock_name = lock_name
        locks.append(YaleLockDevice(f"{lock_name}", client, lock_name, pin))

    async_add_entities(locks, True)


class YaleLockDevice(LockEntity):
    """Representation of an Yale lock."""

    def __init__(self, name, client, lock_name, pin):
        """Initialize the lock."""
        self._name = name
        self._client = client
        self._state = None
        self._lock_name = lock_name
        self._pin = pin

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.name}_lock"

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Return the state of the device."""
        lock_status = self._client.get_locks_status()
        self._state = lock_status[self._lock_name]

    def lock(self, code=None):
        """Send lock command."""
        lock = self._client.lock_api.get(self._lock_name)
        lock.close()

    def unlock(self, code=None):
        """Send unlock command."""
        lock = self._client.lock_api.get(self._lock_name)
        lock.open(pin_code=self._pin)
