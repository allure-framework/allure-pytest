'''
This module contains basic examples of tests
'''
import pytest


def test_success():
    'this test succedes'
    assert True


def test_failure():
    'this test fails'
    assert False


def test_skip():
    'this test is skipped'
    pytest.skip('for a reason!')


@pytest.mark.xfail()
def test_xfail():
    'this test is an xfail'
    assert False


@pytest.mark.xfail()
def test_xpass():
    'this test is a xpass -- it is expected to fail, but still passes'
    assert True


def test_broken_fixture(NOT_A_FIXTURE):
    'this test fails due to a non-satisfiable fixture request'
    assert True


def a_func(x):
    return b_func(x)


def b_func(x):
    raise RuntimeError(x)


def test_long_stacktrace():
    a_func('I am a failure reason')


def test_pytest_expansion():
    a = {1: 2, 3: 4}
    b = {1: 3, 3: 4}

    assert a == b
