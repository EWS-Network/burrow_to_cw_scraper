#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2021 John Mille <john@ews-network.net>

"""Main module."""

import requests


class BurrowQueryV3(object):

    """
    Class to Query the BurrowApi and wrap answers
    `HTTP Endpoints <https://github.com/linkedin/Burrow/wiki/HTTP-Endpoint>__`

    :ivar str url: The URL of the burrow instance
    """

    def __init__(self, url):
        """
        Init.
        """
        self.url = url

    def list_clusters(self, raw=False):
        """
        Method to get the list of clusters
        `Docs <https://github.com/linkedin/Burrow/wiki/http-request-list-clusters>`__

        :return:
        """
        query = requests.get(f"{self.url}/v3/kafka")
        if raw:
            return query
        return query.json()

    def get_cluster_details(self, cluster, raw=False):
        """
        Method to get the list of clusters
        `Docs <https://github.com/linkedin/Burrow/wiki/http-request-kafka-cluster-detail>`__

        :return:
        """
        query = requests.get(f"{self.url}/v3/kafka/{cluster}")
        if raw:
            return query
        return query.json()

    def list_cluster_topics(self, cluster, raw=False):
        """
        Method to get the list of clusters
        `Docs <https://github.com/linkedin/Burrow/wiki/http-request-list-cluster-topics>`__

        :return:
        """
        query = requests.get(f"{self.url}/v3/kafka/{cluster}/topic")
        if raw:
            return query
        return query.json()

    def get_topic_details(self, cluster, topic, raw=False):
        """
        Method to get the list of clusters
        `Docs <https://github.com/linkedin/Burrow/wiki/http-request-get-topic-detail>`__

        :return:
        """
        query = requests.get(f"{self.url}/v3/kafka/{cluster}/topic/{topic}")
        if raw:
            return query
        return query.json()

    def get_consumer_details(self, cluster, group, raw=False):
        """
        Method to get the list of clusters
        `Docs <https://github.com/linkedin/Burrow/wiki/http-request-get-consumer-detail>`__

        :return:
        """
        query = requests.get(f"{self.url}/v3/kafka/{cluster}/consumer/{group}")
        if raw:
            return query
        return query.json()

    def get_consumer_status(self, cluster, group, raw=False):
        """
        Method to get the list of clusters
        `Docs <https://github.com/linkedin/Burrow/wiki/http-request-consumer-group-status>`__

        :return:
        """
        query = requests.get(f"{self.url}/v3/kafka/{cluster}/consumer/{group}/status")
        if raw:
            return query
        return query.json()

    def list_consumers(self, cluster, raw=False):
        """
        Method to get the list of clusters
        `Docs <https://github.com/linkedin/Burrow/wiki/http-request-list-consumers>`__

        :return:
        """
        query = requests.get(f"{self.url}/v3/kafka/{cluster}/consumer")
        if raw:
            return query
        return query.json()

    def delete_consumer(self, cluster, group, raw=False):
        """
        Method to get the list of clusters
        `Docs <https://github.com/linkedin/Burrow/wiki/http-request-remove-consumer-group>`__

        :return:
        """
        query = requests.delete(f"{self.url}/v3/kafka/{cluster}/consumer/{group}")
        if raw:
            return query
        return query.json()
