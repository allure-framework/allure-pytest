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
        print "Hello"
