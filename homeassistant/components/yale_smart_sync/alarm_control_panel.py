"""Component for interacting with the Yale Smart Alarm System API."""
import logging

from yalesmartalarmclient.client import (
    YALE_STATE_ARM_FULL,
    YALE_STATE_ARM_PARTIAL,
    YALE_STATE_DISARM,
)

import homeassistant.components.alarm_control_panel as alarm
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_TRIGGER,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Yale Smart Sync alarm panels based on a config entry."""

    alarms = []

    client = hass.data[DOMAIN][entry.entry_id]

    alarms.append(YaleAlarmDevice("Yale Smart Alarm", client))

    async_add_entities(alarms, True)


class YaleAlarmDevice(alarm.AlarmControlPanelEntity):
    """Represent a Yale Smart Alarm."""

    def __init__(self, name, client):
        """Initialize the Yale Alarm Device."""
        self._name = name
        self._client = client
        self._state = None

        self._state_map = {
            YALE_STATE_DISARM: STATE_ALARM_DISARMED,
            YALE_STATE_ARM_PARTIAL: STATE_ALARM_ARMED_HOME,
            YALE_STATE_ARM_FULL: STATE_ALARM_ARMED_AWAY,
        }

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.name}_alarm"

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY | SUPPORT_ALARM_TRIGGER

    def update(self):
        """Return the state of the device."""
        armed_status = self._client.get_armed_status()

        if self._state is not STATE_ALARM_TRIGGERED:
            self._state = self._state_map.get(armed_status)

    def alarm_disarm(self, code=None):
        """Send disarm command."""
        self._client.disarm()

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        self._client.arm_partial()

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        self._client.arm_full()

    def alarm_trigger(self, code=None):
        """Trigger Panic Button."""
        self._client.trigger_panic_button()
        self._state = STATE_ALARM_TRIGGERED
