"""Support for Yale lock."""
import logging

from yalesmartalarmclient.client import (
    YALE_LOCK_STATE_DOOR_OPEN,
    YALE_LOCK_STATE_LOCKED,
    YALE_LOCK_STATE_UNKNOWN,
    YALE_LOCK_STATE_UNLOCKED,
)

from homeassistant.components.lock import LockEntity
from homeassistant.const import STATE_LOCKED, STATE_OPEN, STATE_UNKNOWN, STATE_UNLOCKED

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Yale locks."""

    locks = []

    client = hass.data[DOMAIN][config_entry.entry_id]

    locks.append(YaleLockDevice("Lock", client))

    async_add_entities(locks, True)


class YaleLockDevice(LockEntity):
    """Representation of an Yale lock."""

    def __init__(self, name, client):
        """Initialize the lock."""
        self._name = name
        self._client = client
        self._state = None

        self._state_map = {
            YALE_LOCK_STATE_DOOR_OPEN: STATE_OPEN,
            YALE_LOCK_STATE_LOCKED: STATE_LOCKED,
            YALE_LOCK_STATE_UNLOCKED: STATE_UNLOCKED,
            YALE_LOCK_STATE_UNKNOWN: STATE_UNKNOWN,
        }

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Return the state of the device."""
        lock_status = self._client.get_locks_status()
        for name in lock_status.keys():
            name = name
        self._state = lock_status[name]

    def lock(self, code=None):
        """Send disarm command."""
        lock = self._client.lock_api.get(name="House")
        lock.close()

    def unlock(self, code="****"):
        """Send arm home command."""
        lock = self._client.lock_api.get(name="House")
        lock.open(pin_code="****")
