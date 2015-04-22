"""
Test for severity markings in allure

Created on Nov 8, 2013

@author: pupssman
"""

from __future__ import absolute_import

import pytest

from hamcrest import assert_that, contains, all_of, has_entry, has_property, has_properties

from allure.constants import Severity, Status
from allure import utils
from .matchers import has_label


def severity_element(value):
    return has_properties(attrib=all_of(has_entry('name', 'severity'),
                                        has_entry('value', value)))


def has_test_with_severity(test_name, severity_level):
    return has_label(test_name, label_value=severity_level, label_name='severity')


@pytest.mark.parametrize('mark_way', ['@pytest.allure.%s',
                                      '@pytest.allure.severity(pytest.allure.severity_level.%s)'
                                      ], ids=['Short', 'Full'])
@pytest.mark.parametrize('name,value', utils.all_of(Severity))
def test_method_severity(report_for, name, value, mark_way):
    report = report_for("""
    import pytest

    %s
    def test_foo():
        pass
    """ % (mark_way % name))

    assert_that(report, has_test_with_severity('test_foo', value))


def test_class_severity(report_for):
    """
    Checks that severity markers for tests override ones for class
    """
    report = report_for("""
    import pytest

    @pytest.allure.severity(pytest.allure.severity_level.CRITICAL)
    class TestMy:

        def test_a(self):
            pass

        @pytest.allure.severity(pytest.allure.severity_level.TRIVIAL)
        def test_b(self):
            pass
    """)

    assert_that(report, all_of(
        has_test_with_severity('TestMy.test_a', Severity.CRITICAL),
        has_test_with_severity('TestMy.test_b', Severity.TRIVIAL),
        has_test_with_severity('TestMy.test_b', Severity.CRITICAL)
    ))


def test_module_severity(report_for):
    """
    Checks severity markers for modules
    """
    report = report_for("""
    import pytest

    pytestmark = pytest.allure.severity(pytest.allure.severity_level.MINOR)

    def test_m():
        pass

    @pytest.allure.severity(pytest.allure.severity_level.NORMAL)
    def test_n():
        pass

    @pytest.allure.severity(pytest.allure.severity_level.CRITICAL)
    class TestMy:

        def test_a(self):
            pass

        @pytest.allure.severity(pytest.allure.severity_level.TRIVIAL)
        def test_b(self):
            pass
    """)

    assert_that(report, all_of(
        has_test_with_severity('test_m', Severity.MINOR),
        has_test_with_severity('test_n', Severity.MINOR),
        has_test_with_severity('test_n', Severity.NORMAL),
        has_test_with_severity('TestMy.test_a', Severity.MINOR),
        has_test_with_severity('TestMy.test_a', Severity.CRITICAL),
        has_test_with_severity('TestMy.test_b', Severity.MINOR),
        has_test_with_severity('TestMy.test_b', Severity.CRITICAL),
        has_test_with_severity('TestMy.test_b', Severity.TRIVIAL)
    ))


@pytest.mark.parametrize('severities', [[Severity.CRITICAL],
                                        [Severity.CRITICAL, Severity.MINOR],
                                        [Severity.CRITICAL, Severity.MINOR, Severity.NORMAL],
                                        [Severity.NORMAL],
                                        [Severity.TRIVIAL],
                                        [Severity.BLOCKER],
                                        ])
def test_run_only(report_for, severities):
    """
    Checks that running for given severities runs only selected tests
    """
    report = report_for("""
    import pytest

    @pytest.allure.CRITICAL
    def test_a():
        pass

    @pytest.allure.MINOR
    def test_b():
        pass

    def test_c():
        pass
    """, extra_run_args=['--allure_severities', ','.join(severities)])

    a_status, b_status, c_status = [Status.PASSED if s in severities else Status.CANCELED for s in [Severity.CRITICAL, Severity.MINOR, Severity.NORMAL]]

    assert_that(report.xpath(".//test-case"), contains(
        all_of(has_property('name', 'test_a'), has_property('attrib', has_entry('status', a_status))),
        all_of(has_property('name', 'test_b'), has_property('attrib', has_entry('status', b_status))),
        all_of(has_property('name', 'test_c'), has_property('attrib', has_entry('status', c_status)))
    ))
