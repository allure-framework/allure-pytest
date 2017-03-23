"""
Test pytest metafunc integrations

Created on Apr 18, 2016

@author: pupssman
"""

from hamcrest import assert_that, contains, has_property


def test_steps_in_parametrize(report_for):
    """
    Test that allure steps do not cause problems in pytest_generate_tests
    """
    report = report_for('''
    import allure

    @allure.step
    def foo():
        return 'hello'

    def pytest_generate_tests(metafunc):
        metafunc.parametrize('val', [foo()])

    def test_foo(val):
        assert val
    ''')

    assert_that(report.findall('.//test-case'), contains(has_property('name', 'test_foo[hello]')))
