"""Main module."""
import logging
from socket import socket, AF_INET, SOCK_DGRAM, \
    SOL_SOCKET, SO_BROADCAST, inet_ntoa


logger = logging.getLogger(__name__)


def find_niko():
    """Locates the niko home control controller"""
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    logger.debug("Sending discover packet")
    sock.sendto(b"D", ("255.255.255.255", 10000))
    logger.debug("Listing for discover answer")
    data, addr = sock.recvfrom(1024)
    logger.debug(f"Discover data {data}")
    ip = inet_ntoa(data[6:10])
    sock.close()
    return ip
