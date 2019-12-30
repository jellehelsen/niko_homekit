"""Module for interacting with Niko Home Control"""
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import logging.config
import json

logging.config.fileConfig("logging.conf", os.environ)
LOGGER = logging.getLogger(__name__)


class Action():
    """Represents a Niko Home Control action

    """
    def __init__(self, id, name):
        super(Action, self).__init__()
        self.device_id = id
        self.name = name


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
        self._buffer = ''

    def connection_made(self, transport):
        LOGGER.debug("connection_made")
        self.transport = transport
        self.connected.set_result(True)

    def data_received(self, data):
        LOGGER.debug("data_received %x", data)
        decoded = data.decode()
        LOGGER.debug("decoded %x", decoded)
        for line in decoded.splitlines(keepends=True):
            LOGGER.debug("line %x", line)
            LOGGER.debug(self._buffer)
            LOGGER.debug("buffer %x", self._buffer)
            self._buffer += line
            LOGGER.debug("buffer %x", self._buffer)
            if self._buffer.endswith('\r\n'):
                LOGGER.debug("buffer ended")
                received = json.loads(self._buffer)
                LOGGER.debug("received %x", received)
                self._buffer = ''
                if 'cmd' in received:
                    LOGGER.debug("Cmd Response %x", received)
                    self.cmd_done.set_result(received['data'])

    async def run_cmd(self, cmd):
        """Run the command"""
        LOGGER.debug("run_cmd %x", cmd)
        await self.connected
        self.cmd_done = asyncio.get_event_loop().create_future()
        self.transport.writelines([json.dumps(cmd).encode()])
        return self.cmd_done


class Niko():
    """
    The Niko Home Control system

    """
    def __init__(self, address, port=8000):
        super(Niko, self).__init__()
        self.address = address
        self.port = port
        self.transport = None
        self.connection_thread = None
        self._actions = None
        self._locations = None
        self.protocol = None
        executor_opts = {'max_workers': None}

        if sys.version_info >= (3, 6):
            executor_opts['thread_name_prefix'] = 'NikoSyncWorker'

        self.executor = ThreadPoolExecutor(**executor_opts)
        self.loop = asyncio.get_event_loop()
        self.loop.set_default_executor(self.executor)

    async def connect(self):
        """Connect to NHC"""
        LOGGER.debug("connecting")
        self.transport, self.protocol = await self.loop.create_connection(
            lambda: NHCProtocol(self.on_close, on_event=self.on_event),
            self.address, self.port)
        LOGGER.debug("connection started")

    def on_close(self, arg):
        """Handle a closed connection"""
        pass

    def on_event(self, arg):
        """Handle events"""
        pass

    async def close(self):
        """Close the connection"""
        LOGGER.debug("Closing transport")
        self.transport.close()
        LOGGER.debug("Shutting down executor")
        self.executor.shutdown()
        LOGGER.debug("Closed")

    async def do_cmd(self, cmd):
        """Do the command"""
        LOGGER.debug("do_cmd %x", cmd)
        return await self.protocol.run_cmd(cmd)

    async def get_locations(self):
        """Return all known locations"""
        if not self._locations:
            self._locations = await self.do_cmd({'cmd': 'listlocations'})
        await self._locations
        return self._locations.result()

    async def get_actions(self):
        """Get the actions from NHC"""
        if not self._actions:
            self._actions = await self.do_cmd({'cmd': 'listactions'})
        await self._actions
        return list(map(lambda action: Action(**action),
                        self._actions.result()))

    async def execute_action(self, action_id=None, value=None):
        """Execute the action on NHC"""
        assert id is not None
        assert value is not None
        result = await self.do_cmd({'cmd': 'executeactions',
                                    'id': action_id,
                                    'value1': value})
        await result
        return result.result()
