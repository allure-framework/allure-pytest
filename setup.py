#!/usr/bin/env python
# -*- coding: utf-8 -*-

PACKAGE = "pytest-allure-adaptor"
VERSION = "1.2.8"

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name=PACKAGE,
    version=VERSION,
    description=("Plugin for py.test to generate allure xml reports"),
    author="revan",
    author_email="revan@yandex-team.ru",
    packages=["allure", "allure.contrib"],
    url="https://github.yandex-team.ru/allure/allure-python",
    long_description=read('README.md'),
    entry_points={'pytest11': ['allure_adaptor = allure.adaptor']},
    install_requires=[
        "lxml>=3.2.0",
        "pytest>=2.4.1"]
)
