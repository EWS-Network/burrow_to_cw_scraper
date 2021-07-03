#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2021 John Mille <john@ews-network.net>

"""Console script for burrow_to_cw_scraper."""

import argparse
import sys

from burrow_to_cw_scraper.burrow_scrapper import ClusterScrapper, BurrowScrapper

def main():
    """Console script for burrow_to_cw_scraper."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into " "burrow_to_cw_scraper.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
