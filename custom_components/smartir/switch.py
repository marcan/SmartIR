import asyncio
import logging

from homeassistant.components.switch import SwitchEntity, PLATFORM_SCHEMA
from homeassistant.helpers.dispatcher import async_dispatcher_connect

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the helper switch platform."""

    if discovery_info is None:
        return

    _LOGGER.debug(f"Setup platform {discovery_info}")
    async_add_entities([SmartIRClimateSwitch(
        discovery_info["climate"],
        discovery_info["toggle"]
        )])

class SmartIRClimateSwitch(SwitchEntity):
    def __init__(self, parent, toggle):
        _LOGGER.debug(f"Create sub toggle {toggle} for SmartIRClimate {parent._name}")
        self.hass = parent.hass
        self._parent = parent
        self._unique_id = self._parent._unique_id + "_" + toggle
        self._toggle = toggle
        self._name = self._parent._name + " " + toggle

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the switch device."""
        return self._name

    async def async_turn_on(self, **kwargs):
        self._parent._toggle_state[self._toggle] = True
        await self._parent.send_command()
        self._parent.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._parent._toggle_state[self._toggle] = False
        await self._parent.send_command()
        self._parent.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        return self._parent._toggle_state[self._toggle]
