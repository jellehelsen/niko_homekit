"""Console script for niko_homekit."""
import os
import asyncio
import logging
import logging.config
import click

from niko_homekit import niko_homekit

logging.config.fileConfig("logging.conf", os.environ)
LOGGER = logging.getLogger(__name__)


async def run():
    """main function"""
    LOGGER.debug("Searching for the Niko Home Controller...")
    niko = niko_homekit.find_niko()
    LOGGER.debug("Controller found at %r", niko.address)
    await niko.connect()
    # start_homekit()
    click.echo("Hello World!")


@click.command()
def main():
    """Console script for niko_homekit."""
    asyncio.run(run())
    return 0
