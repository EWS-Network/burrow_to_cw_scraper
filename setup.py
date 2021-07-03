#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages

DIR_HERE = os.path.abspath(os.path.dirname(__file__))
# REMOVE UNSUPPORTED RST syntax
REF_REGX = re.compile(r"(\:ref\:)")

try:
    with open(f"{DIR_HERE}/README.rst", encoding="utf-8") as readme_file:
        readme = readme_file.read()
        readme = REF_REGX.sub("", readme)
except FileNotFoundError:
    readme = "Burrow to CW scraper"

try:
    with open(f"{DIR_HERE}/HISTORY.rst", encoding="utf-8") as history_file:
        history = history_file.read()
except FileNotFoundError:
    history = "Latest packaged version."

requirements = []
with open(f"{DIR_HERE}/requirements.txt", "r") as req_fd:
    for line in req_fd:
        requirements.append(line.strip())

test_requirements = []
try:
    with open(f"{DIR_HERE}/requirements_dev.txt", "r") as req_fd:
        for line in req_fd:
            test_requirements.append(line.strip())
except FileNotFoundError:
    print("Failed to load dev requirements. Skipping")

setup_requirements = []

requirements = []

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest>=3',
]

setup(
    author="John Preston",
    author_email='john@ews-network.net',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="Application scraping burrow API to publish metrics to AWS CloudWatch",
    entry_points={
        'console_scripts': [
            'burrow_to_cw_scraper=burrow_to_cw_scraper.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='burrow_to_cw_scraper',
    name='burrow_to_cw_scraper',
    packages=find_packages(include=['burrow_to_cw_scraper', 'burrow_to_cw_scraper.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ews-network/burrow_to_cw_scraper',
    version='0.0.1',
    zip_safe=False,
)
