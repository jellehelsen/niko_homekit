"""Console script for niko_homekit."""
# import sys
import click
from socket import socket, AF_INET, SOCK_DGRAM, \
    SOL_SOCKET, SO_BROADCAST, inet_ntoa


def find_niko():
    """Locates the niko home control controller"""
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.sendto(b"D", ("255.255.255.255", 10000))
    data, addr = sock.recvfrom(1024)
    ip = inet_ntoa(data[6:10])
    sock.close()
    return ip


@click.command()
def main(args=None):
    """Console script for niko_homekit."""
    # niko = find_niko()
    # start_niko(niko)
    # start_homekit()
    click.echo("Hello World!")
    return 0
