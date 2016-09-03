"""
Support for interfacing with the XBMC/Kodi JSON-RPC API.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.kodi/
"""
import logging
import urllib

from homeassistant.components.media_player import SUPPORT_SELECT_SOURCE
from homeassistant.components.media_player import kodi


_LOGGER = logging.getLogger(__name__)
REQUIREMENTS = kodi.REQUIREMENTS
SUPPORT_KODI = kodi.SUPPORT_KODI | SUPPORT_SELECT_SOURCE


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Kodi platform."""
    url = '{}:{}'.format(config.get('host'), config.get('port', '8080'))

    jsonrpc_url = config.get('url')  # deprecated
    if jsonrpc_url:
        url = jsonrpc_url.rstrip('/jsonrpc')

    add_devices([
        MyKodiDevice(
            config.get('name', 'Kodi'),
            url,
            auth=(
                config.get('user', ''),
                config.get('password', '')),
            turn_off_action=config.get('turn_off_action', 'none'),
            addons=config.get('addons', None)),
    ])


class MyKodiDevice(kodi.KodiDevice):
    """Representation of a XBMC/Kodi device."""

    # pylint: disable=too-many-public-methods, abstract-method
    # pylint: disable=too-many-instance-attributes
    def __init__(self, name, url, auth=None, turn_off_action=None, addons=None):
        """Initialize the Kodi device."""
        self._selected_addons = addons

        # The last step of init is update, so we'll initialize this last.
        super(MyKodiDevice, self).__init__(name, url, auth, turn_off_action)

    @property
    def supported_media_commands(self):
        """Flag of media commands that are supported."""
        supported_media_commands = (
            super(MyKodiDevice, self).supported_media_commands)
        supported_media_commands |= SUPPORT_KODI

        return supported_media_commands

    @property
    def source_list(self):
        """List of available input addons"""
        self._addons = dict(
                (addon['addonid'].rsplit('.', 1)[-1], addon['addonid'])
                for addon in self._server.Addons.GetAddons()['addons']
                if addon['type'] in ('xbmc.python.script', 'xbmc.python.pluginsource'))
        if self._selected_addons is None:
            return list(self._addons.keys())
        else:
            return self._selected_addons

    def select_source(self, source_name):
        val = self._server.Addons.ExecuteAddon(
            wait=False, addonid=self._addons[source_name])
        _LOGGER.warning([source_name, self._addons[source_name], val])
