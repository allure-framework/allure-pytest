"""
This module holds tests for error messages and stacktraces

Created on Oct 18, 2013

@author: pupssman
"""

from hamcrest import has_property, assert_that, has_properties, has_string, has_entry, all_of
from hamcrest.library.text.stringcontainsinorder import string_contains_in_order

from allure.constants import Status


def has_error(message='', trace='', status=Status.FAILED):
    return has_property('{}test-cases',
                        has_property('test-case',
                                     all_of(has_property('attrib', has_entry('status', status)),
                                            has_property('failure',
                                                         has_properties({'message': message,
                                                                         'stack-trace': has_string(trace)
                                                                         })))))


def test_smoke(report_for):
    report = report_for("""
    def test_X():
        raise RuntimeError("Foo bar baz")
    """)

    assert_that(report, has_error(message='RuntimeError: Foo bar baz',
                                  trace=string_contains_in_order('raise',
                                                                 'RuntimeError("Foo bar baz")',
                                                                 "RuntimeError: Foo bar baz")))


def test_setup_error(report_for):
    report = report_for("""
    import pytest

    @pytest.fixture
    def FOO():
        raise RuntimeError("ololo")

    def test_X(FOO):
        assert True
    """)

    assert_that(report, has_error(message='RuntimeError: ololo',
                                  status=Status.BROKEN,
                                  trace=string_contains_in_order('FOO',
                                                                 'raise',
                                                                 'RuntimeError("ololo")',
                                                                 "RuntimeError: ololo")))


def test_missing_fixture(report_for):
    report = report_for("""
    def test_X(FOO):
        assert True
    """)

    assert_that(report, has_error(message=string_contains_in_order('FixtureLookupError'),
                                  status=Status.BROKEN,
                                  trace=string_contains_in_order("fixture 'FOO' not found",
                                                                 'available fixtures',)))


def test_collect_error(report_for):
    report = report_for("""
    def test_Y():
        foo(
    """)

    assert_that(report, has_error(message='failed',
                                  status=Status.BROKEN,
                                  trace=string_contains_in_order('import',
                                                                 'SyntaxError')))


def test_xpass(report_for):
    report = report_for("""
    import pytest

    @pytest.mark.xfail(strict=True, reason='ololo')
    def test_Y():
        assert True
    """)

    assert_that(report, has_error(message='Failed: [XPASS(strict)] ololo',
                                  trace='[XPASS(strict)] ololo'))


def test_xfail(report_for):
    report = report_for("""
    import pytest

    @pytest.mark.xfail(reason='ololo')
    def test_Y():
        assert False
    """)

    assert_that(report, has_error(message='ololo',
                                  status=Status.PENDING,
                                  trace=string_contains_in_order('assert False',
                                                                 'AssertionError')))


def test_skip(report_for):
    report = report_for("""
    import pytest

    def test_Y():
        pytest.skip('ololo')
    """)

    assert_that(report, has_error(message='Skipped: ololo',
                                  status=Status.CANCELED,
                                  trace=''))


def test_skip_long(report_for):
    report = report_for("""
    import pytest

    def test_Y():
        pytest.skip('ololo' * 16 + '!')
    """)

    assert_that(report, has_error(message='Skipped: ' + 'ololo' * 16 + '...',
                                  status=Status.CANCELED,
                                  trace='Skipped: ' + 'ololo' * 16 + '!'))
