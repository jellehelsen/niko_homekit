#!/usr/bin/env python

"""Tests for `niko_homekit` package."""

import pytest

from click.testing import CliRunner
from unittest.mock import patch
from socket import socket, inet_aton

from niko_homekit import niko_homekit
from niko_homekit import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "Hello World!" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output


@pytest.mark.asyncio
async def test_find_niko(mocker):
    """Test if Niko is found"""
    sock = mocker.patch("niko_homekit.niko_homekit.socket", spec=socket)
    instance = sock.return_value
    return_data = b"D\0\0FFF" + inet_aton("192.168.0.120") + inet_aton("255.255.255.0")
    instance.recvfrom.return_value = (return_data, b"192.168.0.120")
    result = niko_homekit.find_niko()
    assert result.address == "192.168.0.120"
