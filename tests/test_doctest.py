import pytest

from hamcrest import assert_that, contains, all_of, has_entry, has_property, has_properties


def test_doctests(report_for):
    report = report_for("""
    def hello_world():
        '''
        >>> hello_world()
        'hello world'
        '''
        return 'hello world'
    """, ['--doctest-modules'])
    assert_that(report.findall('.//test-case'), contains(
        has_property('description', '[doctest] test_doctests.hello_world')))
