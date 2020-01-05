#!/usr/bin/env python

"""Tests for `niko_homekit` package."""

import pytest
import asyncio
import time

from click.testing import CliRunner
from unittest.mock import patch
from socket import socket, inet_aton, AF_INET, SOCK_DGRAM
from threading import Thread

from concurrent.futures import Future
from niko_homekit import niko_homekit
from niko_homekit import cli
from . import controller, niko


def get_local_address():
    """
    Grabs the local IP address using a socket.
    :return: Local IP Address in IPv4 format.
    :rtype: str
    """
    # TODO: try not to talk 8888 for this
    s = socket(AF_INET, SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        addr = s.getsockname()[0]
    finally:
        s.close()
    return addr


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface(mocker):
    """Test the CLI."""

    def end_cli(done):
        time.sleep(0.2)
        done.set_result(True)

    fut = mocker.patch("niko_homekit.cli.Future")
    done = Future()
    fut.return_value = done
    t = Thread(target=end_cli, args=(done,))
    t.daemon = True
    t.start()
    assert t.is_alive()
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    # assert "Hello World!" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


@pytest.mark.asyncio
async def test_run():
    async def end_run(done):
        await asyncio.sleep(0.2)
        done.set_result(True)

    done = Future()
    asyncio.gather(cli.run(done), end_run(done))


@pytest.mark.asyncio
async def test_find_niko(mocker):
    """Test if Niko is found"""
    sock = mocker.patch("niko_homekit.niko_homekit.socket", spec=socket)
    instance = sock.return_value
    return_data = b"D\0\0FFF" + inet_aton("192.168.0.120") + inet_aton("255.255.255.0")
    instance.recvfrom.return_value = (return_data, b"192.168.0.120")
    result = niko_homekit.find_niko()
    assert result.address == "192.168.0.120"


@pytest.mark.asyncio
async def test_get_accessory_driver(controller, niko):
    driver = await niko_homekit.get_accessory_driver(niko)
    assert driver is not None
    assert driver.accessory is not None
    assert driver.accessory.accessories is not None
    assert len(driver.accessory.accessories) > 0
    print(driver.accessory.accessories)
    key = list(driver.accessory.accessories.keys())[0]
    accessory = driver.accessory.accessories[key]
    accessory.set_bulb(100)


# @pytest.mark.asyncio
# async def test_driver_action(controller):
#     def run_cli(done):
#         asyncio.run(cli.run(done))
#     done = Future()
#     thread = Thread(target=run_cli, args=(done,))
#     thread.start()
#     assert thread.is_alive()
#     time.sleep(.5)
#     done.set_result(True)
