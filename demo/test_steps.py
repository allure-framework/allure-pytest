"""
Demo for steps and nested steps

Created on Nov 6, 2013

@author: pupssman
"""

import pytest


@pytest.mark.parametrize('fail', [True, False])
def test_inline_step(fail):
    """
    has two steps right iside of it
    """
    with pytest.allure.step('First step'):  # @UndefinedVariable
        print 'OLOLO in first step'

    with pytest.allure.step('Second step that fails'):  # @UndefinedVariable
        assert fail


@pytest.mark.parametrize('fail', [True, False])
def test_nested_steps(fail):
    """
    has three nested steps
    """
    with pytest.allure.step('First step'):  # @UndefinedVariable
        with pytest.allure.step('Second step'):  # @UndefinedVariable
            with pytest.allure.step('Third step'):  # @UndefinedVariable
                assert fail


@pytest.fixture(params=[True, False])
def myfixture(request):
    with pytest.allure.step('First Fixture step'):  # @UndefinedVariable
        with pytest.allure.step('Second Fixture step'):  # @UndefinedVariable
            with pytest.allure.step('Third Fixture step'):  # @UndefinedVariable
                assert request.param


def test_fixture(myfixture):
    """
    Has fixture with steps and a separate step.
    Fixture setup fails once.
    """

    with pytest.allure.step('Test step'):  # @UndefinedVariable
        assert True


@pytest.mark.parametrize('fail', [True, False])
def test_step_attach(fail):
    """
    Attaches stuff in steps
    """
    with pytest.allure.step('First step'):  # @UndefinedVariable
        pytest.allure.attach('First attach', 'ololo')  # @UndefinedVariable
        with pytest.allure.step('Second step'):  # @UndefinedVariable
            pytest.allure.attach('Second attach', 'pewpew')  # @UndefinedVariable
            with pytest.allure.step('Third step'):  # @UndefinedVariable
                assert fail


@pytest.allure.step('my func step')
def my_func():
    return 8


def test_decorator():
    """
    Uses a function that is decorated with pytest.allure.step
    """
    assert my_func() > 5
