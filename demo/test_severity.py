"""
Demo tests for serverity markings

Created on Nov 8, 2013

@author: pupssman
"""
import pytest


@pytest.allure.severity(pytest.allure.severity_level.TRIVIAL)  # @UndefinedVariable
def test_trivial():
    assert True


@pytest.allure.severity(pytest.allure.severity_level.BLOCKER)  # @UndefinedVariable
def test_blocker():
    assert True


@pytest.mark.parametrize('run', range(5))
@pytest.allure.severity(pytest.allure.severity_level.CRITICAL)  # @UndefinedVariable
def test_critical(run):
    assert True


@pytest.allure.severity(pytest.allure.severity_level.MINOR)  # @UndefinedVariable
class TestsThatAreMinorByDefault:
    def test_a(self):
        assert True

    def test_b(self):
        assert False

    @pytest.allure.severity(pytest.allure.severity_level.TRIVIAL)  # @UndefinedVariable
    def test_c(self):
        """
        This one is marked as trivial
        """
        assert True


@pytest.allure.BLOCKER
def test_shortcut_blocker():
    pass
