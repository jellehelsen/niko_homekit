#!/usr/bin/env python

import pytest
import json
import threading
from socket import socket
from threading import Thread
from niko_homekit.niko import Niko
from . import controller, niko


def test_controller(controller):
    sock = socket()
    sock.connect(("127.0.0.1", controller.port))
    sock.sendall(b"Hello")
    data = sock.recv(1024)
    assert data == b"Hello\r\n"
    assert len(controller.calls) == 1
    assert controller.calls[0] == "Hello"
    assert controller.connections == 1
    pass


@pytest.mark.asyncio
async def test_connection(controller, niko):
    assert controller.connections == 1
    pass


@pytest.mark.asyncio
async def test_get_locations(controller, niko):
    locations = await niko.get_locations()
    assert len(locations) > 0
    assert locations[0]["id"] == 1
    assert locations[0]["name"] == "location1"
    assert '{"cmd": "listlocations"}' in controller.calls
    assert len(controller.calls) == 1
    # check if caching works
    assert len(locations) > 0
    assert locations[0]["id"] == 1
    assert locations[0]["name"] == "location1"
    assert '{"cmd": "listlocations"}' in controller.calls
    assert len(controller.calls) == 1
    pass


@pytest.mark.asyncio
async def test_get_actions(controller, niko):
    actions = await niko.get_actions()
    assert len(actions) > 0
    assert actions[0].device_id == 1
    assert actions[0].name == "Action 1"
    assert len(controller.calls) == 1
    # check if caching works
    actions = await niko.get_actions()
    assert len(actions) > 0
    assert actions[0].device_id == 1
    assert actions[0].name == "Action 1"
    assert len(controller.calls) == 1
    pass


@pytest.mark.asyncio
async def test_execute_action(controller, niko):
    result = await niko.execute_action(action_id=1, value=100)
    assert result is not None
    assert result == {"error": 0}
    assert len(controller.calls) == 1
    result = await niko.execute_action(action_id=1, value=0)
    assert result is not None
    assert result == {"error": 0}
    assert len(controller.calls) == 2
    pass


# @pytest.mark.asyncio
# async def test_real_action():
#     niko = Niko('192.168.0.141')
#     await niko.connect()
#     result = await niko.execute_action(action_id=1, value=100)
#     assert result is not None
#     assert result == {"error": 0}
#     await asyncio.sleep(1)

#     result = await niko.execute_action(action_id=1, value=0)
#     assert result is not None
#     assert result == {"error": 0}
#     pass
