from abc import ABC, abstractmethod
from base64 import b64encode
import binascii
import requests
import logging
import json
import circa

from homeassistant.const import ATTR_ENTITY_ID
from . import Helper

_LOGGER = logging.getLogger(__name__)

BROADLINK_CONTROLLER = 'Broadlink'
XIAOMI_CONTROLLER = 'Xiaomi'
MQTT_CONTROLLER = 'MQTT'
LOOKIN_CONTROLLER = 'LOOKin'
ESPHOME_CONTROLLER = 'ESPHome'

ENC_BASE64 = 'Base64'
ENC_HEX = 'Hex'
ENC_PRONTO = 'Pronto'
ENC_RAW = 'Raw'
ENC_XIAOMI = 'Xiaomi'
ENC_GENERIC = 'Generic'

CIRCA_ENCODING_MAP = {
    ENC_BASE64: "broadlink",
    ENC_HEX: "broadlink-hex",
    ENC_PRONTO: "pronto",
    ENC_RAW: "rawpm",
}

def get_controller(hass, controller, encoding, controller_data, delay):
    """Return a controller compatible with the specification provided."""
    controllers = {
        BROADLINK_CONTROLLER: BroadlinkController,
        XIAOMI_CONTROLLER: XiaomiController,
        MQTT_CONTROLLER: MQTTController,
        LOOKIN_CONTROLLER: LookinController,
        ESPHOME_CONTROLLER: ESPHomeController
    }
    try:
        return controllers[controller](hass, controller, encoding, controller_data, delay)
    except KeyError:
        raise Exception("The controller is not supported.")


class AbstractController(ABC):
    """Representation of a controller."""
    def __init__(self, hass, controller, encoding, controller_data, delay):
        self.hass = hass
        self._controller = controller
        self._input_encoding = encoding
        if encoding in self.ENCODINGS:
            self._encoding = encoding
        else:
            self._encoding = self.ENCODINGS[0]
        if self._input_encoding in CIRCA_ENCODING_MAP:
            self._circa_input_type = circa.find_format(CIRCA_ENCODING_MAP[self._input_encoding])
        else:
            self._circa_input_type = None
            if self._encoding != self._input_encoding and self._input_encoding != ENC_GENERIC:
                raise Exception(f"Conversion from {self._input_encoding} encoding not supported")

        self._circa_type = circa.find_format(CIRCA_ENCODING_MAP[self._encoding])
        self._controller_data = controller_data
        self._delay = delay

    async def send(self, command):
        """Send a command to the controller."""
        _LOGGER.debug(f"Original command: {command!r}")

        if isinstance(command, circa.IRCode):
            _, _, command = self._circa_type.from_code(command).to_string_parts()
        elif self._input_encoding == ENC_GENERIC:
            _, _, command = self._circa_type.from_code(circa.from_generic(command)).to_string_parts()
        elif self._input_encoding != self._encoding or self._encoding == ENC_RAW: # Always normalize raw codes
            code = self._circa_input_type.from_string(CIRCA_ENCODING_MAP[self._input_encoding], command)
            _, _, command = self._circa_type.from_code(code).to_string_parts()

        _LOGGER.debug(f"--> Converted command: {command!r}")

        return await self._send(command)

    @abstractmethod
    async def _send(self, command):
        """Send a formatted command to the controller."""
        pass


class BroadlinkController(AbstractController):
    """Controls a Broadlink device."""
    ENCODINGS = [ENC_BASE64]

    async def _send(self, command):
        """Send a command."""
        commands = []

        if not isinstance(command, list): 
            command = [command]

        for _command in command:
            commands.append('b64:' + _command)

        service_data = {
            ATTR_ENTITY_ID: self._controller_data,
            'command':  commands,
            'delay_secs': self._delay
        }

        await self.hass.services.async_call(
            'remote', 'send_command', service_data)


class XiaomiController(AbstractController):
    """Controls a Xiaomi device."""
    ENCODINGS = [ENC_PRONTO, ENC_XIAOMI]

    async def _send(self, command):
        """Send a command."""
        service_data = {
            ATTR_ENTITY_ID: self._controller_data,
            'command':  self._encoding.lower().replace("xiaomi", "raw") + ':' + command
        }

        await self.hass.services.async_call(
            'remote', 'send_command', service_data)


class MQTTController(AbstractController):
    """Controls a MQTT device."""
    ENCODINGS = [ENC_RAW]

    async def _send(self, command):
        """Send a command."""
        service_data = {
            'topic': self._controller_data,
            'payload': command
        }

        await self.hass.services.async_call(
            'mqtt', 'publish', service_data)


class LookinController(AbstractController):
    """Controls a Lookin device."""
    ENCODINGS = [ENC_PRONTO, ENC_RAW]

    async def _send(self, command):
        """Send a command."""
        encoding = self._encoding.lower().replace('pronto', 'prontohex')
        url = f"http://{self._controller_data}/commands/ir/" \
                f"{encoding}/{command.replace(",", " ")}"
        await self.hass.async_add_executor_job(requests.get, url)


class ESPHomeController(AbstractController):
    """Controls a ESPHome device."""
    ENCODINGS = [ENC_RAW]

    async def _send(self, command):
        """Send a command."""
        service_data = {'command': json.loads(f"[{command}]")}

        await self.hass.services.async_call(
            'esphome', self._controller_data, service_data)
