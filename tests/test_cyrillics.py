# -*- coding: utf-8 -*-
"""
Test for cyrillics in allure

Created on Oct 19, 2013

@author: pupssman
"""

from hamcrest import has_property, assert_that, contains
from hamcrest.core.core.allof import all_of
from allure.utils import present_exception, unicodify


def test_cyrillic_desc(report_for):
    report = report_for(u"""
    # -*- coding: utf-8 -*-
    def test_foo():
        u'тест с русскоязычным описанием'

        assert True
    """)

    assert_that(report.findall('test-cases'), contains(
                                                       has_property('description', u'тест с русскоязычным описанием')))


def test_cyrillic_exc(report_for):
    report = report_for(u"""
    # -*- coding: utf-8 -*-
    def test_foo():
        raise Exception(u'русские буквы')
    """)

    assert_that(report.findall('.//failure'), contains(
                                                       all_of(has_property('message', u'Exception: русские буквы'),
                                                              has_property('stack-trace', u'''def test_foo():
>       raise Exception(u'русские буквы')
E       Exception: русские буквы

test_cyrillic_exc.py:3: Exception'''))))


def test_unicodify_no_breaks_stuff():
    assert unicodify('<">') == '<">'


def test_complex_exc_xmld_ok():
    assert 'Exception' in present_exception(Exception(u'Помогите'.encode('cp1251')))
