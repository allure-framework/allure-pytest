#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'mavlyutov@yandex-team.ru'

from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import equal_to, has_property, has_properties, has_item, anything


class HasFloat(BaseMatcher):

    def __init__(self, str_matcher):
        self.str_matcher = str_matcher

    def _matches(self, item):
        return self.str_matcher.matches(float(item))

    def describe_to(self, description):
        description.append_text('an object with float ').append_description_of(self.str_matcher)


def has_float(match):
    return HasFloat(wrap_matcher(match))


def has_label(test_name, label_name=anything(), label_value=anything()):
    return has_property('{}test-cases',
                        has_property('test-case',
                                     has_item(
                                         has_properties({'name': equal_to(test_name),
                                                         'labels': has_property('label',
                                                                                has_item(
                                                                                    has_property('attrib', equal_to(
                                                                                        {'name': label_name,
                                                                                         'value': label_value}))))}))))
