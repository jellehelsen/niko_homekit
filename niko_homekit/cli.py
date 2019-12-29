"""Console script for niko_homekit."""
import os
import click
import logging
import logging.config

from niko_homekit import niko_homekit

logging.config.fileConfig("logging.conf", os.environ)
logger = logging.getLogger(__name__)


@click.command()
def main(args=None):
    """Console script for niko_homekit."""
    logger.debug("Searching for the Niko Home Controller...")
    niko = niko_homekit.find_niko()
    logger.debug(f"Controller found at {niko}")
    # start_niko(niko)
    # start_homekit()
    click.echo("Hello World!")
    return 0
