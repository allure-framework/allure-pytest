import pytest

from hamcrest import assert_that, contains, has_property, equal_to


@pytest.mark.parametrize('package', ['pytest.allure', 'allure'])
def test_descriptions(report_for, package):
    report = report_for("""
    import pytest
    import allure

    def test_x():
        %s.description('Description')
    """ % package)

    assert_that(report.findall('.//test-case'),
                contains(has_property('description', equal_to('Description'))))
