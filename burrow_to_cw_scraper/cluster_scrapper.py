#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2021 John Mille <john@ews-network.net>

"""
Module to define the scrapper class and logic
"""

import re
from datetime import datetime as dt
from os import environ

import boto3
from time import sleep

from burrow_to_cw_scraper.aws import get_cross_role_session
from burrow_to_cw_scraper.burrow_client import BurrowQueryV3


class Topic(object):
    def __init__(self, name, group, status, current_lag, partition_data):
        """
        Class to represent a Topic dataset for a consumer group

        :param name:
        :param data:
        """
        self.name = name
        self.group = group
        self.status = status
        self.current_lag_series = []
        self.current_lag_series.append(current_lag)
        self.current_lag = []
        self.partitions = {}
        self.partitions.update(partition_data)
        self.partitions_count = len(self.partitions.keys()) if self.partitions else 0
        self.latest_measure_timestamp = None

    def update_average_lag(self):
        self.current_lag = (
            (sum(self.current_lag_series) / len(self.current_lag_series)) if self.current_lag_series else 0
        )

    def update_partitions_count(self):
        self.partitions_count = len(self.partitions.keys())
        if self.partitions_count < 1:
            raise ValueError(f"Measured no partition. There must be at least 1 partition for {self.name} topic")

    def generate_topic_metrics_data(self):
        """
        Method to produce the datapoints of the PutMetricData
        """


class Consumer(object):
    """
    Class to represent a consumer group and maintain its metadata, and publish metrics
    """

    def __init__(self, name, cluster_name, cw_config, client, session=None):
        """
        Method to initialize the consumer group

        :param BurrowQueryV3 client:
        :param session:
        :param burrow_to_cw_scraper.models.CloudwatchConfig cw_config:
        """
        self.name = name
        self.cluster_name = cluster_name
        self.config = cw_config
        self.client = client
        self.topics = {}
        self.session = session
        self.status = None
        self.region = (
            cw_config.iam.region_name if cw_config.iam.region_name else environ.get("AWS_DEFAULT_REGION", None)
        )
        if self.session is None:
            if not cw_config.iam:
                self.session = boto3.session.Session()
            elif cw_config.iam:
                if cw_config.iam.role_arn:
                    self.session = get_cross_role_session(
                        session=boto3.session.Session(),
                        arn=cw_config.iam.role_arn,
                        session_name=cw_config.iam.session_name,
                    )

    def update_topics_metric_data(self):
        status_r = self.client.get_consumer_status(cluster=self.cluster_name, group=self.name)
        self.status = status_r["status"]["status"]
        partitions = status_r["status"]["partitions"]

        for part in partitions:
            topic_name = part["topic"]
            if topic_name not in self.topics.keys():
                partition = part["partition"]
                timestamp = part["end"]["timestamp"]
                topic = Topic(
                    name=part["topic"],
                    group=self.name,
                    status=part["status"],
                    current_lag=part["current_lag"],
                    partition_data={partition: {"current_lag": part["current_lag"], "timestamp": timestamp}},
                )
                topic.latest_measure_timestamp = part["maxlag"]["end"]["timestamp"]
                self.topics[topic_name] = topic
            else:
                topic = self.topics[topic_name]
                topic.current_lag_series.append(part["current_lag"])
                partition = part["partition"]
                timestamp = part["end"]["timestamp"]
                topic.partitons.update(
                    {partition: {"current_lag": part["partition"]["current_lag"], "timestamp": timestamp}}
                )
                if topic.latest_measure_timestamp < timestamp:
                    topic.latest_measure_timestamp = timestamp

        for topic_name, topic in self.topics.items():
            topic.update_average_lag()
            topic.update_partitions_count()

    def put_metrics(self):
        client = self.session.client("cloudwatch")
        for topic in self.topics.values():
            client.put_metric_data(
                Namespace=self.config.namespace,
                MetricData=[
                    {
                        'MetricName': 'current_lag',
                        'Dimensions': [
                            {'Name': 'cluster', 'Value': self.cluster_name},
                            {"Name": 'group', "Value": self.name},
                            {"Name": "topic", "Value": topic.name},
                        ],
                        'Timestamp': topic.latest_measure_timestamp,
                        'Value': topic.current_lag,
                        'Unit': 'None',
                        'StorageResolution': self.config.interval,
                    },
                ],
            )
            for p_id, partition in topic.partitions.items():
                client.put_metric_data(
                    Namespace=self.config.namespace,
                    MetricData=[
                        {
                            'MetricName': 'current_lag',
                            'Dimensions': [
                                {'Name': 'cluster', 'Value': self.cluster_name},
                                {"Name": 'group', "Value": self.name},
                                {"Name": "topic", "Value": topic.name},
                                {"Name": "partition_id", "Value": f"{topic.name}_{p_id}"},
                            ],
                            'Timestamp': partition["timestamp"],
                            'Value': partition["current_lag"],
                            'Unit': 'None',
                            'StorageResolution': self.config.interval,
                        },
                    ],
                )
        self.topics.clear()


class ClusterScrapper(object):
    """
    Class to scrape consumer groups information

    :ivar timestamp: Timestamp tracker to refresh information on Interval
    :ivar list consumer_names: The list of consumers to maintain for the cluster based on configuration
    """

    def __init__(self, cluster, client):
        """
        Method to init a new scrapper

        :param BurrowQueryV3 client:
        :param burrow_to_cw_scraper.models.cluster.Spec cluster:
        """
        self.cluster = cluster
        self.client = client
        self.consumers_names = []
        self.timestamp = dt.utcnow()
        self.define_monitored_consumers()
        self.consumers = []
        self.init_consumers()

    def define_monitored_consumers(self):
        consumers_r = self.client.list_consumers(cluster=self.cluster.name)
        if "consumers" not in consumers_r or not consumers_r["consumers"]:
            raise KeyError(f"No consumers where retrieved for {self.cluster.name}")
        tmp_consumers = consumers_r["consumers"]
        if self.cluster.config.groups_blacklist_regex:
            drop_re = re.compile(self.cluster.config.groups_blacklist_regex)
            tmp_consumers[:] = [x for x in tmp_consumers if not drop_re.match(x)]
        if self.cluster.config.groups_blacklist:
            tmp_consumers[:] = [x for x in tmp_consumers if x not in self.cluster.config.groups_blacklist]
        if self.cluster.config.groups_regex:
            accept_re = re.compile(self.cluster.config.groups_regex)
            for consumer_name in tmp_consumers:
                if accept_re.match(consumer_name) or consumer_name in self.cluster.config.groups:
                    self.consumers_names.append(consumer_name)

    def init_consumers(self):
        for consumer in self.consumers_names:
            self.consumers.append(Consumer(consumer, self.cluster.name, self.cluster.config.cloudwatch, self.client))
