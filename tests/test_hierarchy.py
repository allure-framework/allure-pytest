"""
These tests check TestSuite generation and test placement

Created on Oct 14, 2013

@author: pupssman
"""

from hamcrest import assert_that, contains, has_property, has_properties, contains_inanyorder


def test_two_files(reports_for):
    reports = reports_for(test_foo="""
    def test_A():
        pass
    """, test_bar="""
    def test_B():
        pass
    """)

    assert_that([r.findall('.//test-case') for r in reports], contains_inanyorder(
        contains(has_property('name', 'test_B')),
        contains(has_property('name', 'test_A')),
    ))


def test_class(report_for):
    report = report_for("""
    class TestFoo:
        def test_A(self):
            pass
    """)

    assert_that(report.findall('.//test-case'), contains(has_property('name', 'TestFoo.test_A')))


def test_nested_class(report_for):
    report = report_for("""
    class TestFoo:
        class TestBar:
            def test_A(self):
                pass
    """)

    assert_that(report.findall('.//test-case'), contains(has_property('name', 'TestFoo.TestBar.test_A')))


def test_single_suite_params(report_for):
    report = report_for(test_my_suite="""
    'test suite for foo'

    def test():
        pass
    """)

    assert_that(report, has_properties({'{}name': 'test_my_suite', '{}description': 'test suite for foo'}))


def test_two_suite_params(reports_for):
    reports = reports_for(test_A="""
    'suite_A'

    def test():
        pass
    """, test_B="""
    'suite_B'
    def test():
        pass""")

    assert_that(reports, contains_inanyorder(
        has_properties({'{}name': 'test_A', '{}description': 'suite_A'}),
        has_properties({'{}name': 'test_B', '{}description': 'suite_B'}),
    ))
