#!/usr/bin/env python
# -*- coding: utf-8 -*-

PACKAGE = "pytest-allure-adaptor"
VERSION = "1.3.5"

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name=PACKAGE,
    version=VERSION,
    description=("Plugin for py.test to generate allure xml reports"),
    author="pupssman",
    author_email="pupssman@yandex-team.ru",
    packages=["allure", "allure.contrib"],
    url="https://github.com/allure-framework/allure-python",
    long_description=read('README.md'),
    entry_points={'pytest11': ['allure_adaptor = allure.pytest_plugin']},
    install_requires=[
        "lxml>=3.2.0",
        "pytest>=2.4.1"]
)
