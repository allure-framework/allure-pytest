"""
This module holds tests for compatibility with other py.test plugins.

Created on Apr 15, 2014

@author: pupssman
"""

from hamcrest import assert_that, contains, has_property


def test_maxfail(report_for):
    """
    Check that maxfail generates proper report
    """
    report = report_for("""
    def test_a():
        assert False

    def test_b():
        assert True
    """, extra_run_args=['-x'])

    assert_that(report.findall('.//test-case'), contains(has_property('name', 'test_a')))
