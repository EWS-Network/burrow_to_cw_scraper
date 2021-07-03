#!/usr/bin/env python

"""Tests for `burrow_to_cw_scraper` package."""


import pytest
from os import path
import yaml

from burrow_to_cw_scraper import burrow_client
from burrow_to_cw_scraper.models import Config


HERE = path.abspath(path.dirname(__file__))


def test_normal_config():
    with open(f"{HERE}/../use-cases/config.yaml") as config_fd:
        content = yaml.load(config_fd.read())
    the_config = Config.parse_obj(content)
    print(the_config.json())
