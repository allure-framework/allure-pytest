import pytest
import allure


@pytest.fixture(scope='session')
def allure_test_fixture():
    return allure_test_fixture_impl()


class allure_test_fixture_impl():

    @allure.step('allure_test_fixture_step')
    def test(self):
        print "Hello"
