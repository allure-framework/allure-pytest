# encoding: utf-8

"""
Tests for steps with allure-adaptor

Created on Nov 3, 2013

@author: pupssman
"""
from __future__ import absolute_import

import time

from hamcrest import assert_that, has_property, has_entry, has_properties, contains
from hamcrest.library.number.ordering_comparison import greater_than_or_equal_to, \
    less_than_or_equal_to
from hamcrest.core.core.allof import all_of
from .matchers import has_float
from allure.constants import Status
import pytest


def step_with(name, start, stop, status):
    return has_properties(name=name,
                          title=name,
                          attrib=all_of(has_entry('start', has_float(greater_than_or_equal_to(start))),
                                        has_entry('stop', has_float(less_than_or_equal_to(stop))),
                                        has_entry('status', status)))


@pytest.fixture()
def timed_report_for(report_for):
    def impl(*a, **kw):
        start = time.time() * 1000
        report = report_for(*a, **kw)
        stop = time.time() * 1000

        return report, start, stop

    return impl


@pytest.mark.parametrize('status,expr', [(Status.PASSED, 'assert True'),
                                         (Status.FAILED, 'assert False'),
                                         (Status.CANCELED, 'pytest.skip("foo")'),
                                         (Status.PENDING, 'pytest.xfail("foo")'), ])
def test_one_step(timed_report_for, status, expr):
    report, start, stop = timed_report_for("""
    import pytest
    def test_ololo_pewpew():
        with pytest.allure.step(title='my_fancy_step'):
            %s
    """ % expr)

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with(name='my_fancy_step',
                                                                              start=start,
                                                                              stop=stop,
                                                                              status=status)))


def test_single_step(timed_report_for):
    report, start, stop = timed_report_for("""
    import pytest
    def test_ololo_pewpew():
         pytest.allure.single_step(text='single_step')
    """)

    assert_that(report.findall('.//test-case/steps/step'),
                contains(step_with(name='single_step',
                                   start=start,
                                   stop=stop,
                                   status=Status.PASSED)))


def test_two_steps(timed_report_for):
    report, start, stop = timed_report_for("""
    import pytest
    def test_ololo_pewpew():
        with pytest.allure.step(title='step_1'):
            assert True

        with pytest.allure.step(title='step_2'):
            assert False
    """)

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with('step_1', start, stop, Status.PASSED),
                                                                    step_with('step_2', start, stop, Status.FAILED)))


def test_fixture_step(timed_report_for):
    report, start, stop = timed_report_for("""
    import pytest

    @pytest.fixture
    def afixture():
        with pytest.allure.step(title='fixture'):
            return 1

    def test_ololo_pewpew(afixture):
        assert afixture
    """)

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with('fixture', start, stop, Status.PASSED)))


def test_other_module_fixture_step(testdir, timed_report_for):
    fixture_def_body = """
from __future__ import print_function
import pytest
import allure

@pytest.fixture(scope='session')
def allure_test_fixture():
    '''
    This is a fixture used by test checking lazy initialization of steps context.
    It must be in a separate module, to be initialized before pytest configure stage.
    Don't move it to tests code.
    '''
    return allure_test_fixture_impl()


class allure_test_fixture_impl():

    @allure.step('allure_test_fixture_step')
    def test(self):
        print("Hello")

"""
    testdir.makepyfile(util_fixture=fixture_def_body)
    testdir.makeconftest("pytest_plugins = 'util_fixture'")

    report, start, stop = timed_report_for("""
    import pytest

    def test_other_module_fixture(allure_test_fixture):
        allure_test_fixture.test()
    """)

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with('allure_test_fixture_step', start, stop, Status.PASSED)))


def test_nested_steps(timed_report_for):
    report, start, stop = timed_report_for("""
    import pytest
    def test_ololo_pewpew():
        with pytest.allure.step(title='outer'):
            with pytest.allure.step(title='inner'):
                assert False

    """)

    assert_that(report.findall('.//test-case/steps/step'), contains(all_of(step_with('outer', start, stop, Status.FAILED),
                                                                           has_property('steps',
                                                                                        has_property('step',
                                                                                                     step_with('inner', start, stop, Status.FAILED))))))


def test_step_attach(timed_report_for):
    report, start, stop = timed_report_for("""
    import pytest
    def test_ololo_pewpew():
        with pytest.allure.step(title='withattach'):
            pytest.allure.attach('myattach', 'abcdef')
    """)

    assert_that(report.findall('.//test-case/steps/step'), contains(all_of(step_with('withattach', start, stop, Status.PASSED),
                                                                           has_property('attachments',
                                                                                        has_property('attachment',
                                                                                                     has_entry('title', 'myattach'))))))


@pytest.mark.parametrize('package', ['pytest.allure', 'allure'])
def test_step_function_decorator(timed_report_for, package):
    report, start, stop = timed_report_for("""
    import pytest
    import allure

    @%s.step('step_foo')
    def foo(bar):
        return bar

    def test_ololo_pewpew():
        assert foo(123)
    """ % package)

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with('step_foo', start, stop, Status.PASSED)))


@pytest.mark.parametrize('statement, expected_name', [('("ololo")', 'ololo'), ('', 'foo')])
def test_step_function_default_name(timed_report_for, statement, expected_name):
    report, start, stop = timed_report_for("""
    import pytest
    import allure

    @allure.step%s
    def foo(bar):
        return bar

    def test_ololo_pewpew():
        assert foo(123)
    """ % statement)

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with(expected_name, start, stop, Status.PASSED)))


def test_step_fixture_decorator(timed_report_for):
    report, start, stop = timed_report_for("""
    import pytest

    @pytest.allure.step('fixture_step_foo')
    @pytest.fixture()
    def foo():
        return 123

    def test_ololo_pewpew(foo):
        assert foo
    """)

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with('fixture_step_foo', start, stop, Status.PASSED)))


def test_step_fixture_method(timed_report_for):
    report, start, stop = timed_report_for("""
    import pytest

    class MyImpl:
        def __init__(self):
            pass

        @pytest.allure.step('fixture_step_bar')
        def bar(self, x):
            return x

    @pytest.fixture()
    def foo():
        return MyImpl()

    def test_ololo_pewpew(foo):
        assert foo.bar(5) == 5
    """)

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with('fixture_step_bar', start, stop, Status.PASSED)))


@pytest.mark.parametrize('step_name,value,expected_name',
                         [('"X:{0}"', '"abc"', 'X:abc'),
                          ('u"{0}"', u'u"тест"', u'тест'),
                          ('"{foo}:{bar}"', 'foo=123, bar="x"', '123:x'),
                          ('"{0!r}"', '"abc"', "'abc'"),
                          ('"{0[a]}"', '{"a": "b"}', "b"),
                          ('"{0}-{1}"', '123, 456', "123-456"),
                          ])
def test_step_decorator_formatting(timed_report_for, step_name, value, expected_name):
    report, start, stop = timed_report_for(u"""
    # encoding: utf-8
    import pytest
    import allure

    @allure.step(%s)
    def foo(*a, **kw):
        return True

    def test_ololo_pewpew():
        assert foo(%s)
    """ % (step_name, value))

    assert_that(report.findall('.//test-case/steps/step'), contains(step_with(expected_name, start, stop, Status.PASSED)))
