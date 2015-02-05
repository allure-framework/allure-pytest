"""
These tests check schema correctness and basic values

Created on Oct 14, 2013

@author: pupssman
"""

from __future__ import absolute_import

import os
import time
import pytest

from hamcrest import is_, assert_that, contains, has_property, all_of, has_entry, greater_than, less_than, \
    has_entries, contains_inanyorder, is_not, has_items, starts_with
from allure.constants import Status
from .matchers import has_float


@pytest.mark.parametrize('statement', ['assert 1', 'assert 0',
                                       'pytest.xfail()', 'pytest.skip()',
                                       'foo('])
def test_smoke_simple(report_for, statement):
    report = report_for("""
    import pytest
    def test():
        %s
    """ % statement)

    assert_that(report.findall('.//test-case'), contains(has_property('name')))


@pytest.mark.parametrize('test', ['def test_foo(not_a_funcarg)',
                                  '@pytest.mark.xfail()\n    def test_xfail()',
                                  '@pytest.mark.skipif(1, reason="foo")\n    def test_skip()',
                                  ])
def test_smoke_decorated_success(report_for, test):
    report = report_for("""
    import pytest
    %s:
        assert 0
    """ % test)

    assert_that(report.findall('.//test-case'), contains(has_property('name')))


def test_one_success(report_for):
    report = report_for("""
    def test_baz():
        'ololo a docstring'
        assert 1
    """)

    assert_that(report.findall('.//test-case'), contains(all_of(
        has_property('name', 'test_baz'),
        has_property('description', 'ololo a docstring'),
        has_entry('status', Status.PASSED),
    )))


def test_one_failure(report_for):
    report = report_for("""
    def test_fail():
        'fail test dosctring'
        assert 0
    """)

    assert_that(report.findall('.//test-case'), contains(all_of(
        has_property('name', 'test_fail'),
        has_property('description', 'fail test dosctring'),
        has_entry('status', Status.FAILED),
        has_property('failure',
                     all_of(has_property('message'),
                            has_property('stack-trace')))
    )))


def test_suite_times(report_for):
    start = time.time()

    report = report_for("""
    def test():
        assert True
    """)

    stop = time.time()

    assert_that(report.get('start'), has_float(all_of(
        greater_than(start * 1000),
        less_than(float(report.get('stop')))
    )))

    assert_that(report.get('stop'), has_float(all_of(
        greater_than(float(report.get('start'))),
        less_than(stop * 1000),
    )))


@pytest.mark.parametrize('stmt', ['assert True',
                                  'assert False',
                                  'foo('])
def test_test_times(report_for, stmt):
    start = time.time()

    report = report_for("""
    def test():
        %s
    """ % stmt)

    stop = time.time()

    assert_that(report.find('.//test-case').attrib, has_entries(start=has_float(greater_than(start * 1000)),
                                                                stop=has_float(less_than(stop * 1000))))


def test_collection_error(report_for):
    report = report_for(test_broken_module="""
    def test(
    """)

    assert_that(report, all_of(
        has_property('{}test-cases', has_property('test-case', contains(
            has_property('{}name', 'test_broken_module')))),
        has_property('{}title', 'Collection phase')))


@pytest.mark.parametrize('test', ['assert 0', 'assert 1'])
def test_attaches_with_capture_exist(report_for, test):
    report = report_for("""
    import sys
    def test_x():
        sys.stdout.write('STDOUT HELLO')
        sys.stderr.write('STDERR HELLO')
        %s
    """ % test)

    assert_that(report.find('.//attachment'), contains_inanyorder(
        has_entry('title', starts_with('Captured stdout')),
        has_entry('title', starts_with('Captured stderr'))))


@pytest.mark.parametrize('channel', ['err', 'out'])
def test_attach_contents(report_for, channel):
    report = report_for("""
    import sys
    def test_x():
        sys.std%s.write('OLOLO PEWPEW')
    """ % channel)

    attach = report.find('.//attachment').get('source')

    assert_that(open(os.path.join('my_report_dir', attach)).read(), is_('OLOLO PEWPEW'))


def test_report_directory_cleanup(report_for, reportdir):
    report_for("""
    def test():
        assert True
    """)
    a = os.listdir(str(reportdir))

    report_for("""
    def test():
        assert False
    """)
    b = os.listdir(str(reportdir))

    assert_that(b, is_not(has_items(*a)))
