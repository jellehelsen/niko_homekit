"""Console script for niko_homekit."""
import os
import asyncio
import logging
import logging.config
from concurrent.futures import Future
import click

from niko_homekit import niko_homekit

# logging.config.fileConfig("logging.conf", os.environ, disable_existing_loggers=False)
LOGGER = logging.getLogger(__name__)


async def run(done):
    """main function"""
    LOGGER.debug("Searching for the Niko Home Controller...")
    niko = niko_homekit.find_niko()
    LOGGER.debug("Controller found at %r", niko.address)
    await niko.connect()
    LOGGER.debug("Getting driver")
    driver = await niko_homekit.get_accessory_driver(niko)
    LOGGER.debug("Driver instanciated")
    driver.add_job(driver._do_start)  # pylint: disable=protected-access
    await asyncio.wrap_future(done)
    await driver.async_stop()


@click.command()
def main():
    """Console script for niko_homekit."""
    try:
        done = Future()
        print(done)
        loop = asyncio.new_event_loop()
        loop.create_task(run(done))
        loop.run_forever()
    except KeyboardInterrupt:
        done.set_result(True)
    return 0
