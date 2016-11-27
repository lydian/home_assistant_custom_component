"""
Support for interface with a Panasonic Viera TV.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.panasonic_viera/
"""
import logging
import socket
import subprocess

import voluptuous as vol

from homeassistant.components.media_player import SUPPORT_TURN_ON, DOMAIN, PLATFORM_SCHEMA
from homeassistant.components.media_player import panasonic_viera
from homeassistant.const import (
    CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON, STATE_UNKNOWN)
import homeassistant.helpers.config_validation as cv

CONF_PORT = panasonic_viera.CONF_PORT

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = panasonic_viera.REQUIREMENTS

DEFAULT_NAME = 'Panasonic Viera TV'
DEFAULT_PORT = 55000

SUPPORT_VIERATV = panasonic_viera.SUPPORT_VIERATV | SUPPORT_TURN_ON

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
})

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Panasonic Viera TV platform."""
    from panasonic_viera import DEFAULT_PORT, RemoteControl

    name = config.get(CONF_NAME, 'Panasonic Viera TV')
    port = config.get(CONF_PORT, DEFAULT_PORT)

    if discovery_info:
        _LOGGER.debug('%s', discovery_info)
        vals = discovery_info.split(':')
        if len(vals) > 1:
            port = vals[1]

        host = vals[0]
        remote = RemoteControl(host, port)
        add_devices([MyPanasonicVieraTVDevice(name, remote)])
        return True

    host = config.get(CONF_HOST, None)
    remote = RemoteControl(host, port)
    
    try:
        remote.get_mute()
    except (socket.timeout, TimeoutError, OSError):
        _LOGGER.error('Panasonic Viera TV is not available at %s:%d',
                      host, port)

    add_devices([MyPanasonicVieraTVDevice(name, remote)])
    return True


# pylint: disable=abstract-method
class MyPanasonicVieraTVDevice(panasonic_viera.PanasonicVieraTVDevice):
    """Representation of a Panasonic Viera TV."""

    # pylint: disable=too-many-public-methods
    def __init__(self, name, remote):
        """Initialize the samsung device."""
        # Overwrite the default status, so that when tv is off, we still
        # have the card on the control app.
        super(MyPanasonicVieraTVDevice, self).__init__(name, remote)
        self._playing = True
        self._state = STATE_OFF

    @property
    def supported_media_commands(self):
        """Flag of media commands that are supported."""
        return SUPPORT_VIERATV

    def turn_on(self):
        value = subprocess.call([
            'irsend', '-d', '/var/run/lirc/lircd-lirc0',
            'SEND_ONCE', 'PANASONIC', 'KEY_POWER'])
        _LOGGER.debug('%s', value)
