# -*- coding: utf-8 -*-

'''
Tests for environment parameters

@author: svchipiga
'''

from six import iterkeys, itervalues

import os

import pytest
from hamcrest import has_property, assert_that, equal_to
from hamcrest.core.core.allof import all_of


def first_key(d):
    return next(iterkeys(d))


def first_value(d):
    return next(itervalues(d))


@pytest.mark.parametrize("env_dict", ({'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'c': 3}))
def test_store_environment_with_given_number_of_parameters(allure_impl, env_dict, environment_xml):
    allure_impl.environment.update(env_dict)
    allure_impl.store_environment()
    assert_that(len(environment_xml().findall('.//parameter')), equal_to(len(env_dict)))


@pytest.mark.parametrize("env_dict", ({'me': 42}, {'foo': 'bar'}, {'foo': u'бар'}))
def test_store_environment_if_not_empty(allure_impl, env_dict, environment_xml):
    allure_impl.environment.update(env_dict)
    allure_impl.store_environment()
    assert_that(environment_xml().findall('.//parameter')[0], all_of(has_property('name', first_key(env_dict)),
                                                                     has_property('key', first_key(env_dict)),
                                                                     has_property('value', first_value(env_dict))))


@pytest.mark.parametrize("result", ("True", "False"), ids=("passed", "failed"))
def test_add_environment_in_testcase(report_for, result, environment_xml):
    report_for("""
    import pytest
    import allure

    def test_dummy():
        allure.environment(foo='bar')
        assert %s
    """ % result)

    assert_that(environment_xml().findall('.//parameter')[0], all_of(has_property('name', 'foo'),
                                                                     has_property('key', 'foo'),
                                                                     has_property('value', 'bar')))


def test_environment_not_write_in_pytest(report_for, reportdir, properties_file_name):
    report_for("""
    def test_passed():
        assert True
    """)

    assert not os.path.isfile(os.path.join(str(reportdir), properties_file_name))
