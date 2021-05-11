"""Doorsensor Support for the Nuki Lock."""

import logging

from yalesmartalarmclient.client import YALE_DOOR_CONTACT_STATE_OPEN

from homeassistant.components.binary_sensor import DEVICE_CLASS_DOOR, BinarySensorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Yale Door Contact binary sensor."""

    door_contacts = []

    client = hass.data[DOMAIN][config_entry.entry_id]

    door_contacts_status = await hass.async_add_executor_job(client.get_doors_status)
    for door_contact in door_contacts_status:
        door_contact = door_contact
        door_contacts.append(
            YaleDoorsensorEntity(f"{door_contact}", client, door_contact)
        )

    async_add_entities(door_contacts, True)


class YaleDoorsensorEntity(BinarySensorEntity):
    """Representation of a Yale Contact Doorsensor."""

    def __init__(self, name, client, door_contact):
        """Initialize the Door Contact."""
        self._name = name
        self._client = client
        self._door_contact = door_contact

    @property
    def name(self):
        """Return the name of the doorsensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.name}_doorsensor"

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Return the state of the device."""
        door_contact_status = self._client.get_doors_status()
        self._state = door_contact_status[self._door_contact]

    @property
    def door_sensor_state_name(self):
        """Return the state name of the door sensor."""
        return self._door_contact

    @property
    def is_on(self):
        """Return true if the door is open."""
        return self._door_contact == YALE_DOOR_CONTACT_STATE_OPEN

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_DOOR
