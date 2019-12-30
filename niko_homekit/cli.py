"""Console script for niko_homekit."""
import os
import logging
import logging.config
import click

from niko_homekit import niko_homekit

logging.config.fileConfig("logging.conf", os.environ)
LOGGER = logging.getLogger(__name__)


@click.command()
def main():
    """Console script for niko_homekit."""
    LOGGER.debug("Searching for the Niko Home Controller...")
    niko = niko_homekit.find_niko()
    LOGGER.debug("Controller found at %x", niko)
    # start_niko(niko)
    # start_homekit()
    click.echo("Hello World!")
    return 0
