#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2021 John Mille <john@ews-network.net>

import boto3
from botocore.exceptions import ClientError


def get_cross_role_session(session, arn, session_name=None):
    """
    Function to override ComposeXSettings session to specific session for Lookup

    :param boto3.session.Session session: The original session fetching the credentials for X-Role
    :param str arn:
    :param str session_name: Override name of the session
    :return: boto3 session from lookup settings
    :rtype: boto3.session.Session
    """
    if not session_name:
        session_name = "ComposeX@Lookup"
    try:
        if not session:
            session = boto3.session.Session()
        creds = session.client("sts").assume_role(
            RoleArn=arn,
            RoleSessionName=session_name,
            DurationSeconds=900,
        )
        return boto3.session.Session(
            aws_access_key_id=creds["Credentials"]["AccessKeyId"],
            aws_session_token=creds["Credentials"]["SessionToken"],
            aws_secret_access_key=creds["Credentials"]["SecretAccessKey"],
        )
    except ClientError:
        raise
