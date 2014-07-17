"""
Test for labels markings in allure

Created on Jun 5, 2014

@author: F1ashhimself
"""

from hamcrest import assert_that, equal_to, none, has_length


def collect_labels_from_report(report):
    tests = dict()
    for test_case in report.xpath('.//test-case'):
        for label in test_case.labels.label:
            tests.setdefault(test_case.name, list())
            tests[test_case.name].append((label.attrib['name'],
                                         label.attrib['value']))

    return tests


def collect_failure_messages_from_report(report):
    tests = dict()
    for test_case in report.xpath('.//test-case'):
        tests[test_case.name] = test_case.failure['stack-trace'] if hasattr(test_case, 'failure') else None

    return tests


def test_feature_and_stories(report_for):
    """
    Checks that feature and stories markers for tests are shown in report.
    """
    report = report_for("""
    import pytest

    @pytest.allure.feature('Feature1')
    class TestMy:

        @pytest.allure.story('Story1')
        def test_a(self):
            pass
    """)

    labels = zip(report.xpath('.//test-case/labels/label/@name'),
                 report.xpath('.//test-case/labels/label/@value'))

    assert_that(labels, equal_to([('allure_feature', 'Feature1'),
                                  ('allure_story', 'Story1')]))


def test_feature_and_stories_inheritance(report_for):
    """
    Checks that feature and stories markers can be inherited.
    """
    report = report_for("""
    import pytest

    pytestmark = pytest.allure.feature('Feature1')

    @pytest.allure.feature('Feature2')
    class TestMy:

        @pytest.allure.story('Story1')
        def test_a(self):
            pass

        def test_b(self):
            pass
    """)

    tests = collect_labels_from_report(report)
    expected_labels_a = [('allure_feature', 'Feature2'), ('allure_feature', 'Feature1'),
                         ('allure_story', 'Story1')]
    expected_labels_b = [('allure_feature', 'Feature2'), ('allure_feature', 'Feature1')]

    assert_that(tests['TestMy.test_a'], has_length(len(expected_labels_a)))
    assert_that(tests['TestMy.test_b'], has_length(len(expected_labels_b)))

    assert_that(tests['TestMy.test_a'], equal_to(expected_labels_a))
    assert_that(tests['TestMy.test_b'], equal_to(expected_labels_b))


def test_multiple_features_and_stories(report_for):
    """
    Checks that we can handle multiple feature and stories markers.
    """
    report = report_for("""
    import pytest

    @pytest.allure.feature('Feature1', 'Feature2')
    def test_a():
        pass

    @pytest.allure.story('Story1', 'Story2')
    def test_b():
        pass
    """)

    tests = collect_labels_from_report(report)
    expected_labels_a = [('allure_feature', 'Feature1'), ('allure_feature', 'Feature2')]
    expected_labels_b = [('allure_story', 'Story1'), ('allure_story', 'Story2')]

    assert_that(tests['test_a'], has_length(len(expected_labels_a)))
    assert_that(tests['test_b'], has_length(len(expected_labels_b)))

    assert_that(tests['test_a'], equal_to(expected_labels_a))
    assert_that(tests['test_b'], equal_to(expected_labels_b))


def test_specified_feature_and_story(report_for):
    """
    Checks that tests with specified Feature or Story marks will be run.
    """
    report = report_for("""
    import pytest

    @pytest.allure.feature('Feature1')
    @pytest.allure.story('Story1', 'Story2')
    def test_a():
        pass

    @pytest.allure.feature('Feature1')
    @pytest.allure.feature('Feature2')
    @pytest.allure.story('Story1')
    def test_b():
        pass

    def test_c():
        pass
    """, extra_run_args=['--allure_features', 'Feature1',
                         '--allure_stories', 'Story1,Story2'])

    tests = collect_failure_messages_from_report(report)

    assert_that(tests['test_a'], none())
    assert_that(tests['test_b'], none())
    assert_that(tests['test_c'],
                equal_to("Skipped: Not suitable with selected labels: "
                         "('allure_feature', 'feature1'), ('allure_story', "
                         "'story1'), ('allure_story', 'story2')."))
