"""
Test for severity markings in allure

Created on Nov 8, 2013

@author: pupssman
"""

from hamcrest import assert_that, contains, all_of, has_entry, has_property
from allure.constants import Severity, Status
from allure import utils
import pytest


@pytest.mark.parametrize('mark_way', [
                                      '@pytest.allure.%s',
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

    assert_that(report.xpath(".//test-case/@severity"), contains(value))


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

    assert_that(report.xpath(".//test-case/@severity"), contains(Severity.CRITICAL, Severity.TRIVIAL))


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

    assert_that(report.xpath(".//test-case/@severity"), contains(Severity.MINOR, Severity.NORMAL, Severity.CRITICAL, Severity.TRIVIAL))


@pytest.mark.parametrize('severities', [
                                       [Severity.CRITICAL],
                                       [Severity.CRITICAL, Severity.MINOR],
                                       [Severity.CRITICAL, Severity.MINOR, Severity.NORMAL],
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

    def test_b():
        pass

    @pytest.allure.MINOR
    def test_c():
        pass
    """, extra_run_args=['--allure_severities', ','.join(severities)])

    a_status, b_status, c_status = [Status.PASSED if s in severities else Status.SKIPPED for s in [Severity.CRITICAL, Severity.NORMAL, Severity.MINOR]]

    assert_that(report.xpath(".//test-case"), contains(all_of(has_property('name', 'test_a'),
                                                            has_property('attrib', has_entry('status', a_status))),
                                                     all_of(has_property('name', 'test_b'),
                                                            has_property('attrib', has_entry('status', b_status))),
                                                     all_of(has_property('name', 'test_c'),
                                                            has_property('attrib', has_entry('status', c_status)))))
