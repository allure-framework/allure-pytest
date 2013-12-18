# -*- coding: utf-8 -*-
"""
Test for cyrillics in allure

Created on Oct 19, 2013

@author: pupssman
"""

from hamcrest import has_property, assert_that, contains


def test_foo(report_for):
    report = report_for(u"""
    # -*- coding: utf-8 -*-
    def test_foo():
        u'тест с русскоязычным описанием'

        assert True
    """)

    assert_that(report.findall('test-cases'), contains(
                                                       has_property('description', u'тест с русскоязычным описанием')))
