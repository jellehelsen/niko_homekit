"""Unit test package for niko_homekit."""
import pytest
import json
import threading
from socket import socket
from threading import Thread
from niko_homekit.niko import Niko


class MockNikoController(object):
    """Mocks a Niko Home Control controller

    """

    def __init__(self):
        super(MockNikoController, self).__init__()
        self.sock = socket()
        self.sock.bind(("127.0.0.1", 0))
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
                        if "cmd" in parsed:
                            result = {"cmd": parsed["cmd"]}
                            print(result)
                            if parsed["cmd"] == "listlocations":
                                result["data"] = [
                                    {"id": 1, "name": "location1"},
                                    {"id": 2, "name": "location2"},
                                ]
                                conn.sendall(json.dumps(result).encode() + b"\r\n")
                            elif parsed["cmd"] == "listactions":
                                result["data"] = [
                                    {
                                        "id": 1,
                                        "name": "Action 1",
                                        "value1": 0,
                                        "type": 1,
                                    },
                                    {
                                        "id": 2,
                                        "name": "Action 2",
                                        "value1": 0,
                                        "type": 1,
                                    },
                                ]
                                conn.sendall(json.dumps(result).encode() + b"\r\n")
                            elif parsed["cmd"] == "executeactions":
                                result["data"] = {"error": 0}
                                conn.sendall(json.dumps(result).encode() + b"\r\n")
                            else:
                                conn.sendall(data.encode() + b"\r\n")
                    except ConnectionResetError:
                        break
                    except json.JSONDecodeError:
                        if data:
                            conn.sendall(data.encode() + b"\r\n")
                        pass
        except ConnectionAbortedError as e:
            print("Closing conn")
            if not self._stop:
                raise (e)
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


@pytest.fixture
async def niko(controller):
    niko = Niko("127.0.0.1", controller.port)
    await niko.connect()
    yield niko
    await niko.close()
