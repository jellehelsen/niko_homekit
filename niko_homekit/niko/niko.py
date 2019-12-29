import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import logging.config
import json

logging.config.fileConfig("logging.conf", os.environ)
logger = logging.getLogger(__name__)


class NHCProtocol(asyncio.Protocol):
    """The Niko Home Control protocol v1

    """
    def __init__(self, on_close, on_event=None):
        super(NHCProtocol, self).__init__()
        self.on_close = on_close
        self.on_event = on_event
        self.connected = asyncio.get_running_loop().create_future()
        self._buffer = ''
        pass

    def connection_made(self, transport):
        logger.debug("connection_made")
        self.transport = transport
        self.connected.set_result(True)
        pass

    def data_received(self, data):
        logger.debug(f"data_received {data}")
        decoded = data.decode()
        logger.debug(f"decoded {repr(decoded)}")
        for line in decoded.splitlines(keepends=True):
            logger.debug(f"line {repr(line)}")
            logger.debug("buffer??")
            logger.debug(self._buffer)
            logger.debug(f"buffer {repr(self._buffer)}")
            self._buffer += line
            logger.debug(f"buffer {repr(self._buffer)}")
            if self._buffer.endswith('\r\n'):
                logger.debug(f"buffer ended")
                received = json.loads(self._buffer)
                logger.debug(f"received {received}")
                self._buffer = ''
                if 'cmd' in received:
                    logger.debug(f"Cmd Response {received}")
                    self.cmd_done.set_result(received['data'])
        pass

    async def run_cmd(self, cmd):
        logger.debug(f"run_cmd {cmd}")
        await self.connected
        self.cmd_done = asyncio.get_event_loop().create_future()
        self.transport.writelines([json.dumps(cmd).encode()])
        return self.cmd_done
        pass


class Niko(object):
    """
    The Niko Home Control system

    """
    def __init__(self, address, port=8000):
        super(Niko, self).__init__()
        self.address = address
        self.port = port
        self.transport = None
        self.connection_thread = None
        executor_opts = {'max_workers': None}

        if sys.version_info >= (3, 6):
            executor_opts['thread_name_prefix'] = 'NikoSyncWorker'

        self.executor = ThreadPoolExecutor(**executor_opts)
        self.loop = asyncio.get_event_loop()
        self.loop.set_default_executor(self.executor)

        pass

    async def connect(self):
        logger.debug("connecting")
        self.transport, self.protocol = await self.loop.create_connection(
            lambda: NHCProtocol(self.on_close, on_event=self.on_event),
            self.address, self.port)
        logger.debug("connection started")
        pass

    def on_close(self, arg):
        pass

    def on_event(self, arg):
        pass

    async def close(self):
        logger.debug("Closing transport")
        self.transport.close()
        logger.debug("Shutting down executor")
        self.executor.shutdown()
        logger.debug("Closed")
        pass

    async def do(self, cmd):
        logger.debug(f"do {cmd}")
        return await self.protocol.run_cmd(cmd)

    async def get_locations(self):
        locations = await self.do({'cmd': 'listlocations'})
        await locations
        return locations.result()
