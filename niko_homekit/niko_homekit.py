"""Main module."""
import logging
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM,
    SOL_SOCKET,
    SO_BROADCAST,
    inet_ntoa,
)

from pyhap.accessory_driver import AccessoryDriver
from pyhap.accessory import Accessory, Bridge
from .niko import Niko


LOGGER = logging.getLogger(__name__)


class Lightbulb(Accessory):
    """Documentation for Lightbulb

    """

    def __init__(self, *args, device=None, **kwargs):
        super(Lightbulb, self).__init__(*args, **kwargs)
        self._device = device
        serv_light = self.add_preload_service("Lightbulb")
        self.char_on = serv_light.configure_char(
            "On", value=device.value, setter_callback=self.set_bulb
        )

    def set_bulb(self, value):
        """Set the bulb value"""
        if value:
            LOGGER.debug("turn light %d on", self._device.device_id)
            return self._device.set_value(100)
        LOGGER.debug("turn light %d off", self._device.device_id)
        return self._device.set_value(0)


def find_niko():
    """Locates the niko home control controller"""
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    LOGGER.debug("Sending discover packet")
    sock.sendto(b"D", ("255.255.255.255", 10000))
    LOGGER.debug("Listing for discover answer")
    data, _ = sock.recvfrom(1024)
    LOGGER.debug("Discover data %r", data)
    ip_address = inet_ntoa(data[6:10])
    sock.close()
    return Niko(ip_address)


async def get_accessory_driver(niko):
    """Get the HAP driver"""
    driver = AccessoryDriver(port=51826, loop=niko.loop)
    bridge = Bridge(driver, "Bridge")
    actions = await niko.get_actions()
    for action in actions:
        if action.device_type == 1:
            light = Lightbulb(driver, action.name, device=action)
            bridge.add_accessory(light)

    driver.add_accessory(accessory=bridge)

    return driver
