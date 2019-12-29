#!/usr/bin/env python

import pytest
import json
from socket import socket
from threading import Thread

from niko_homekit.niko.niko import Niko


class MockNikoController(object):
    """Mocks a Niko Home Control controller

    """
    def __init__(self):
        super(MockNikoController, self).__init__()
        self.sock = socket()
        self.sock.bind(('127.0.0.1', 0))
        self.sock.listen(1)
        self.sock.settimeout(1)
        self._stop = False
        self.calls = []
        self.connections = 0
        pass

    @property
    def port(self):
        return self.sock.getsockname()[1]

    def _start(self):
        try:
            conn, addr = self.sock.accept()
            with conn:
                self.connections += 1
                while not self._stop:
                    try:
                        data = conn.recv(1024).decode()
                        self.calls.append(data)
                        if not data:
                            break
                        print(data)
                        parsed = json.loads(data)
                        print(parsed)
                        if 'cmd' in parsed:
                            result = {'cmd': parsed['cmd']}
                            print(result)
                            if parsed['cmd'] == 'listlocations':
                                result['data'] = [
                                    {'id': 1, 'name': "location1"},
                                    {'id': 2, 'name': 'location2'}
                                ]
                                print(result)
                                conn.sendall(json.dumps(result).encode()
                                             + b"\r\n")
                            else:
                                conn.sendall(data.encode()+b"\r\n")
                    except ConnectionResetError:
                        break
                    except json.JSONDecodeError:
                        if data:
                            conn.sendall(data.encode()+b"\r\n")
                        pass
        except ConnectionAbortedError as e:
            print("Closing conn")
            if not self._stop:
                raise(e)
        return

    def start(self):
        self.thread = Thread(target=self._start, daemon=True)
        return self.thread.start()

    def shutdown(self):
        print("Shutting down MockNikoController")
        self._stop = True
        self.sock.close()
        self.thread.join(2)
        print("Stopped MockNikoController")
        return


@pytest.fixture
def controller():
    _controller = MockNikoController()
    _controller.start()
    yield _controller
    _controller.shutdown()


def test_controller(controller):
    sock = socket()
    sock.connect(('127.0.0.1', controller.port))
    sock.sendall(b"Hello")
    data = sock.recv(1024)
    assert data == b"Hello\r\n"
    assert len(controller.calls) == 1
    assert controller.calls[0] == "Hello"
    assert controller.connections == 1
    pass


@pytest.fixture
async def niko(controller):
    niko = Niko('127.0.0.1', controller.port)
    await niko.connect()
    yield niko
    await niko.close()


@pytest.mark.asyncio
async def test_connection(controller, niko):
    assert controller.connections == 1
    pass


@pytest.mark.asyncio
async def test_get_locations(controller, niko):
    locations = await niko.get_locations()
    assert len(locations) > 0
    assert locations[0]['id'] == 1
    assert '{"cmd": "listlocations"}' in controller.calls
    pass
