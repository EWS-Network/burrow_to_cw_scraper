#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2021 John Mille <john@ews-network.net>


import json
from os import path

from time import sleep
import yaml

from burrow_to_cw_scraper.burrow_client import BurrowQueryV3
from burrow_to_cw_scraper.cluster_scrapper import ClusterScrapper
from burrow_to_cw_scraper.models import Config


class BurrowScrapper(object):

    """
    Class to scrape consumer groups information
    """

    def __init__(self, config_path=None, config_raw=None):
        """
        Initialize the scrapper
        """
        self.config = None
        self.cluster_scrapers = []
        if config_raw is None and config_path is None:
            raise KeyError("You must specify at least config_path or config_raw")
        elif config_raw and not config_path:
            self.config = Config.parse_raw(config_raw)
        elif config_path and not config_raw:
            assert path.exists(config_path)
            assert not path.isdir(config_path)
            with open(config_path, "r") as config_fd:
                try:
                    content = yaml.load(config_fd.read(), Loader=yaml.Loader)
                except yaml.YAMLError:
                    content = json.loads(config_fd.read())
            self.config = Config.parse_obj(content)
        self.client = BurrowQueryV3(url=self.config.url)
        for cluster in self.config.clusters:
            if not cluster.config.cloudwatch:
                cluster.config.cloudwatch = self.config.cloudwatch
            scrapper = ClusterScrapper(cluster, self.client)
            scrapper.define_monitored_consumers()
            scrapper.init_consumers()
            self.cluster_scrapers.append(scrapper)

    def scrape(self):
        while 42:
            for scraper in self.cluster_scrapers:
                for consumer in scraper.consumers:
                    consumer.update_topics_metric_data()
                    consumer.put_metrics()
            sleep(min([c.config.cloudwatch.interval for c in self.config.clusters]))
