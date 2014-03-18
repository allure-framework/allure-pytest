from allure.pytest_plugin import MASTER_HELPER


# allow using allure.step decorator instead of pytest.allure.step
step = MASTER_HELPER.step
attach = MASTER_HELPER.attach
