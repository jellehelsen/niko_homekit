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


LOGGER = logging.getLogger(__name__)


def find_niko():
    """Locates the niko home control controller"""
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    LOGGER.debug("Sending discover packet")
    sock.sendto(b"D", ("255.255.255.255", 10000))
    LOGGER.debug("Listing for discover answer")
    data, _ = sock.recvfrom(1024)
    LOGGER.debug("Discover data %x", data)
    ip_address = inet_ntoa(data[6:10])
    sock.close()
    return ip_address
