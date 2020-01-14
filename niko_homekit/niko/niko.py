"""Module for interacting with Niko Home Control"""
import sys
import asyncio
import logging
import logging.config
import json
from concurrent.futures import ThreadPoolExecutor
from aiocache import cached

# logging.config.fileConfig("logging.conf", os.environ)
LOGGER = logging.getLogger(__name__)


class Action:
    """Represents a Niko Home Control action

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, device, controller):
        super(Action, self).__init__()
        self.device_id = device["id"]
        self.name = device["name"]
        self.value = device["value1"]
        self.device_type = device["type"]
        self.controller = controller

    def set_value(self, value):
        """Set the value of the device"""
        self.controller.set_action_value(self.device_id, value)


class NHCProtocol(asyncio.Protocol):
    """The Niko Home Control protocol v1

    """

    def __init__(self, on_close, on_event=None):
        super(NHCProtocol, self).__init__()
        self.on_close = on_close
        self.on_event = on_event
        self.connected = asyncio.get_running_loop().create_future()
        self.transport = None
        self.cmd_done = None
        self._buffer = ""

    def connection_made(self, transport):
        LOGGER.debug("connection_made")
        self.transport = transport
        self.connected.set_result(True)

    def data_received(self, data):
        LOGGER.debug("data_received %r", data)
        decoded = data.decode()
        LOGGER.debug("decoded %r", decoded)
        for line in decoded.splitlines(keepends=True):
            LOGGER.debug("line %r", line)
            LOGGER.debug(self._buffer)
            LOGGER.debug("buffer %r", self._buffer)
            self._buffer += line
            LOGGER.debug("buffer %r", self._buffer)
            if self._buffer.endswith("\r\n"):
                LOGGER.debug("buffer ended")
                received = json.loads(self._buffer)
                LOGGER.debug("received %r", received)
                self._buffer = ""
                if "cmd" in received:
                    LOGGER.debug("Cmd Response %r", received)
                    self.cmd_done.set_result(received["data"])

    async def run_cmd(self, cmd):
        """Run the command"""
        LOGGER.debug("run_cmd %r", cmd)
        await self.connected
        self.cmd_done = asyncio.get_event_loop().create_future()
        self.transport.writelines([json.dumps(cmd).encode()])
        return self.cmd_done


class Niko:
    """
    The Niko Home Control system

    """

    def __init__(self, address, port=8000):
        super(Niko, self).__init__()
        self.address = address
        self.port = port
        self.transport = None
        self.protocol = None
        executor_opts = {"max_workers": None}

        if sys.version_info >= (3, 6):
            executor_opts["thread_name_prefix"] = "NikoSyncWorker"

        self.executor = ThreadPoolExecutor(**executor_opts)
        self.loop = asyncio.get_event_loop()
        self.loop.set_default_executor(self.executor)

    async def connect(self):
        """Connect to NHC"""
        LOGGER.debug("connecting")
        self.transport, self.protocol = await self.loop.create_connection(
            lambda: NHCProtocol(self.on_close, on_event=self.on_event),
            self.address,
            self.port,
        )
        LOGGER.debug("connection started")

    def on_close(self, arg):
        """Handle a closed connection"""

    def on_event(self, arg):
        """Handle events"""

    async def close(self):
        """Close the connection"""
        LOGGER.debug("Closing transport")
        self.transport.close()
        LOGGER.debug("Shutting down executor")
        self.executor.shutdown()
        LOGGER.debug("Closed")

    async def do_cmd(self, cmd):
        """Do the command"""
        LOGGER.debug("do_cmd %r", cmd)
        return await self.protocol.run_cmd(cmd)

    @cached()
    async def get_locations(self):
        """Return all known locations"""
        locations = await self.do_cmd({"cmd": "listlocations"})
        await locations
        return locations.result()

    @cached()
    async def get_actions(self):
        """Get the actions from NHC"""
        actions = await self.do_cmd({"cmd": "listactions"})
        await actions
        return list(map(lambda action: Action(action, self), actions.result()))

    async def execute_action(self, action_id, value):
        """Execute the action on NHC"""
        LOGGER.debug("execute_action %d, %d", action_id, value)
        assert id is not None
        assert value is not None
        LOGGER.debug("execute_action %d, %d", action_id, value)
        result = await self.do_cmd(
            {"cmd": "executeactions", "id": action_id, "value1": value}
        )
        await result
        return result.result()

    def set_action_value(self, action_id, value):
        """Set the value of an action"""
        LOGGER.debug("setting value of action %d to %d", action_id, value)
        coro = self.execute_action(action_id, value)
        asyncio.run_coroutine_threadsafe(coro, self.loop)
